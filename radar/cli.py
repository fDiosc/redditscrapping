import typer
from rich.console import Console
from radar.storage.db import init_db
from radar.storage.vectors import get_or_create_collection
from radar.config import SUBREDDITS

app = typer.Typer()
console = Console()

@app.command()
def init():
    """Initialize database and vector store."""
    console.print("[yellow]Initializing Radar...[/yellow]")
    init_db()
    get_or_create_collection()
    console.print("[green]✓ Database and Vector collection initialized.[/green]")

@app.command()
def ingest(subreddit: str = None, days: int = 7, scraper: bool = False):
    """Ingest posts from subreddits."""
    from radar.ingest.reddit_api import RedditAPI
    from radar.ingest.reddit_scraper import RedditScraper
    from radar.storage.db import init_db
    
    # Auto-initialize database tables if they don't exist
    init_db()
    
    subs = [subreddit] if subreddit else SUBREDDITS.keys()
    
    if scraper:
        client = RedditScraper()
        console.print("[blue]Using Scraper fallback...[/blue]")
    else:
        try:
            client = RedditAPI()
            console.print("[blue]Using Reddit API...[/blue]")
        except Exception as e:
            console.print(f"[red]API Error: {e}. Use --scraper for fallback.[/red]")
            return

    for sub in subs:
        console.print(f"Scraping r/{sub}...")
        count = client.fetch_subreddit_posts(sub, days=days)
        console.print(f"[green]✓ Ingested {count} posts from r/{sub}.[/green]")

@app.command()
def process(batch: int = 50, ai_analyze: bool = True):
    """Process pending posts: generate embeddings, semantic fit, and signals."""
    from radar.storage.db import get_unprocessed_posts, get_connection
    from radar.process.embeddings import get_embeddings
    from radar.process.signals import detect_signals, calculate_intensity, classify_relevance
    from radar.process.ai_analysis import analyze_post_with_ai
    from radar.process.semantic import SemanticEngine
    from radar.storage.vectors import get_or_create_collection, add_embeddings
    from radar.products import AI_ANALYSIS_THRESHOLD
    import json
    
    posts = get_unprocessed_posts()
    if not posts:
        console.print("[green]All posts are already processed.[/green]")
        return
        
    console.print(f"Processing [bold]{len(posts)}[/bold] posts in batches of {batch}...")
    
    # Initialize Engines
    engine = SemanticEngine()
    collection = get_or_create_collection()
    conn = get_connection()
    cursor = conn.cursor()
    
    for i in range(0, len(posts), batch):
        current_batch = posts[i:i+batch]
        texts = [f"{p['title']} {p['body']}" for p in current_batch]
        
        # 1. Generate Embeddings
        try:
            embeddings = get_embeddings(texts)
            ids = [p['id'] for p in current_batch]
            
            sanitized_metadatas = []
            for p in current_batch:
                clean_meta = {k: (v if v is not None else "") for k, v in p.items() if k not in ['embedding_id', 'ai_analysis', 'semantic_similarity', 'community_score']}
                sanitized_metadatas.append(clean_meta)
                
            add_embeddings(collection, ids, embeddings, sanitized_metadatas, texts)
        except Exception as e:
            console.print(f"[red]Embedding error: {e}[/red]")
            continue
            
        # 2. Hybrid Analysis
        for post, text, emb in zip(current_batch, texts, embeddings):
            signals = detect_signals(text)
            
            # Semantic Similarity (Product Fit)
            # Default to profitdoctor if no match found manually
            product_key = next(iter(signals['product_matches'].keys())) if signals['product_matches'] else "profitdoctor"
            similarity = engine.get_product_fit(emb, product_key)
            
            # Community Intensity
            community_score = calculate_intensity(post)
            
            # Intent Bonus
            intent_bonus = classify_relevance(post, signals)
            
            # Hybrid Calculation
            # Formula: (Similarity * 15) + Intent + Community
            relevance = (similarity * 15.0) + intent_bonus + community_score
            
            ai_result = None
            if ai_analyze and relevance >= AI_ANALYSIS_THRESHOLD:
                console.print(f"  [cyan]AI Analyzing High-Relevance post: {post['title'][:50]}... (Similarity: {similarity:.2f})[/cyan]")
                ai_result = analyze_post_with_ai(post, product_key)
            
            cursor.execute("""
                UPDATE posts 
                SET embedding_id = ?, pain_signals = ?, intent = ?, 
                    relevance_score = ?, ai_analysis = ?, 
                    semantic_similarity = ?, community_score = ?,
                    last_processed_score = ?, last_processed_comments = ?
                WHERE id = ?
            """, (post['id'], json.dumps(signals), ",".join(signals['intents']), 
                  relevance, ai_result, similarity, community_score,
                  post['score'], post['num_comments'], post['id']))
            
        conn.commit()
        console.print(f"[green]✓ Processed batch {i//batch + 1}[/green]")
        
    conn.close()

@app.command()
def report(product: str, mode: str = "DIRECT_FIT", limit: int = 15):
    """Generate a calibrated report using different discovery modes."""
    from radar.storage.db import get_connection
    import pandas as pd
    from radar.products import AI_ANALYSIS_THRESHOLD
    
    console.print(f"Generating [bold]{mode}[/bold] report for [bold]{product}[/bold]...")
    conn = get_connection()
    
    # Discovery Mode Logic
    if mode == "DIRECT_FIT":
        # Prioritize Semantic Similarity
        order_by = "semantic_similarity DESC, community_score DESC"
        where_clause = "semantic_similarity > 0.4"
    elif mode == "OPPORTUNITY":
        # Look for adjacent problems (mid-similarity, high intent)
        order_by = "relevance_score DESC"
        where_clause = "semantic_similarity BETWEEN 0.25 AND 0.45"
    elif mode == "INTENSITY":
        # Prioritize where most people are talking
        order_by = "community_score DESC, semantic_similarity DESC"
        where_clause = "community_score > 2"
    else:
        order_by = "relevance_score DESC"
        where_clause = "relevance_score > 0"

    query = f"SELECT * FROM posts WHERE {where_clause} ORDER BY {order_by} LIMIT {limit}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        console.print(f"[yellow]No posts found for mode {mode}. Try a different mode.[/yellow]")
        return
        
    output_path = f"outputs/reports/{product}_{mode.lower()}_report.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Radar Report: {product.capitalize()} ({mode})\n\n")
        f.write(f"> **Mode**: {mode}\n")
        f.write(f"> **Threshold**: AI analysis for relevance >= {AI_ANALYSIS_THRESHOLD}\n\n")
        
        for _, row in df.iterrows():
            f.write(f"## {row['title']}\n")
            f.write(f"- **Relevance**: {row['relevance_score']:.2f} (Fit: {row['semantic_similarity']:.2f} | Intensity: {row['community_score']:.2f})\n")
            f.write(f"- **Link**: [Reddit]({row['url']})\n")
            f.write(f"- **Intent**: {row['intent']}\n\n")
            
            if row['ai_analysis']:
                f.write(f"### 🤖 AI Insight\n{row['ai_analysis']}\n\n")
            
            f.write(f"### Context (Original Post)\n{row['body'][:600]}...\n\n---\n")
            
    console.print(f"[green]✓ {mode} report generated at {output_path}[/green]")

@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Start the Radar API server."""
    import uvicorn
    console.print(f"Starting Radar API server at [bold]http://{host}:{port}[/bold]...")
    uvicorn.run("radar.api.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    app()
