import typer
from typing import List, Optional, Dict, Any
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
def process(ai_analyze: bool = False, batch: int = 50, target_product: str = None, subreddit_filter: List[str] = None, limit: int = None, force: bool = False):
    """Process pending posts: generate embeddings, semantic fit, and signals."""
    from radar.storage.db import get_unprocessed_posts, get_connection
    from radar.process.embeddings import get_embeddings
    from radar.process.signals import detect_signals, calculate_intensity, classify_relevance
    from radar.process.ai_analysis import analyze_post_with_ai
    from radar.process.semantic import SemanticEngine
    from radar.storage.vectors import get_or_create_collection, add_embeddings
    from radar.products import AI_ANALYSIS_THRESHOLD
    import json
    
    posts = get_unprocessed_posts(subreddit_filter=subreddit_filter, limit=limit, force=force)
    if not posts:
        console.print("[green]All specified posts are already processed.[/green]")
        return
        
    console.print(f"Processing [bold]{len(posts)}[/bold] posts in batches of {batch}...")
    if target_product:
        console.print(f"Target Product for AI Analysis: [cyan]{target_product}[/cyan]")
    
    # Initialize Engines
    engine = SemanticEngine()
    collection = get_or_create_collection()
    conn = get_connection()
    cursor = conn.cursor()
    
    for i in range(0, len(posts), batch):
        current_batch = posts[i:i+batch]
        
        # 1. Fetch comments and build Unified Context for each post in batch (Smart Truncation)
        from radar.storage.db import get_comments
        from radar.process.truncation import build_unified_context
        batch_texts = []
        for p in current_batch:
            comments = get_comments(p['id'])
            unified = build_unified_context(p, comments)
            batch_texts.append(unified)
            
        # 2. Generate Embeddings
        try:
            embeddings = get_embeddings(batch_texts)
            ids = [p['id'] for p in current_batch]
            
            sanitized_metadatas = []
            for p in current_batch:
                clean_meta = {k: (v if v is not None else "") for k, v in p.items() if k not in ['embedding_id', 'ai_analysis', 'semantic_similarity', 'community_score']}
                sanitized_metadatas.append(clean_meta)
                
            add_embeddings(collection, ids, embeddings, sanitized_metadatas, batch_texts)
        except Exception as e:
            console.print(f"[red]Embedding error: {e}[/red]")
            continue
            
        # 3. Hybrid Analysis
        from radar.storage.db import save_analysis, get_products
        available_products = get_products()
        
        for post, unified_text, emb in zip(current_batch, batch_texts, embeddings):
            signals = detect_signals(unified_text, available_products=available_products)
            community_score = calculate_intensity(post)
            
            # Analyze for ALL products found in DB
            for p_rec in available_products:
                product_key = p_rec['id']
                similarity = engine.get_product_fit(emb, product_key)
                intent_bonus = classify_relevance(post, signals)
                
                # Formula: (Similarity * 15) + Intent + Community
                relevance = (similarity * 15.0) + intent_bonus + community_score
                
                ai_result = None
                # Step 5: Efficient AI Triggering (Minimum Fit Threshold)
                AI_MINIMUM_FIT = 0.4
                
                should_ai_analyze = ai_analyze and relevance >= AI_ANALYSIS_THRESHOLD and similarity >= AI_MINIMUM_FIT
                if target_product and product_key != target_product:
                    should_ai_analyze = False
                
                if should_ai_analyze:
                    console.print(f"  [cyan]AI Analyzing for {product_key}: {post['title'][:40]}... (Sim: {similarity:.2f})[/cyan]")
                    ai_result = analyze_post_with_ai(unified_text, p_rec)
                
                # Save to specific analysis table
                save_analysis(post['id'], product_key, {
                    "relevance_score": relevance,
                    "semantic_similarity": similarity,
                    "community_score": community_score,
                    "ai_analysis": ai_result,
                    "signals_json": json.dumps(signals)
                }, cursor=cursor)

            # Update master post record state
            try:
                cursor.execute("""
                    UPDATE posts 
                    SET last_processed_score = ?, last_processed_comments = ?
                    WHERE id = ?
                """, (post['score'], post['num_comments'], post['id']))
            except:
                pass
            
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
    from radar.storage.db import get_product
    product_rec = get_product(product)
    if not product_rec:
        console.print(f"[red]Error: Product '{product}' not found in database.[/red]")
        return
        
    conn = get_connection()
    
    # Discovery Mode Logic
    if mode == "DIRECT_FIT":
        # Prioritize Semantic Similarity
        order_by = "pa.semantic_similarity DESC, pa.community_score DESC"
        where_clause = "pa.semantic_similarity >= 0.3"
    elif mode == "OPPORTUNITY":
        # Look for adjacent problems (mid-similarity, high intent)
        order_by = "pa.relevance_score DESC"
        where_clause = "pa.semantic_similarity BETWEEN 0.15 AND 0.4"
    elif mode == "INTENSITY":
        # Prioritize where most people are talking
        order_by = "pa.community_score DESC, pa.semantic_similarity DESC"
        where_clause = "pa.community_score >= 0.5"
    else:
        order_by = "pa.relevance_score DESC"
        where_clause = "pa.relevance_score > 0"

    query = f"""
        SELECT 
            p.id, p.title, p.url, p.body, p.source, p.created_at, p.intent,
            pa.relevance_score, pa.semantic_similarity, pa.community_score, pa.ai_analysis
        FROM posts p
        JOIN post_analysis pa ON p.id = pa.post_id
        WHERE pa.product_id = ? AND {where_clause} 
        ORDER BY {order_by} 
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn, params=(product,))
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
