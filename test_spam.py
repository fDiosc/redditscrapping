"""Force AI reanalysis on high-scoring posts to test spam detection."""
from radar.storage.db import get_connection, save_analysis
from radar.process.ai_analysis import analyze_post_with_ai
from radar.storage.db import get_product
import sqlite3

# Get product info
product = get_product('sonarpro')
if not product:
    print("Product not found")
    exit()

conn = get_connection()
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Find high-scoring posts that already have AI analysis
c.execute('''
    SELECT pa.post_id, pa.relevance_score, pa.semantic_similarity, 
           p.title, p.body, p.author
    FROM post_analysis pa
    JOIN posts p ON p.id = pa.post_id
    WHERE pa.product_id = 'sonarpro' 
    AND pa.relevance_score >= 15
    AND pa.ai_analysis IS NOT NULL
    ORDER BY pa.relevance_score DESC 
    LIMIT 20
''')
rows = c.fetchall()

print(f"Found {len(rows)} high-scoring posts to reanalyze...")

from radar.storage.db import get_comments
from radar.process.truncation import build_unified_context

for row in rows:
    post_id = row['post_id']
    print(f"\n🔄 Reanalyzing: {row['title'][:50]}...")
    print(f"   Score: {row['relevance_score']:.1f} | Fit: {row['semantic_similarity']:.2f}")
    
    # Build context
    post = dict(row)
    post['id'] = post_id
    comments = get_comments(post_id)
    unified = build_unified_context(post, comments)
    
    # Run AI analysis with new prompt
    result = analyze_post_with_ai(unified, product)
    print(f"   ✅ Done!")
    
    # Parse and check spam
    import json
    try:
        ai = json.loads(result)
        if ai.get('is_spam_or_ad'):
            print(f"   ⚠️  SPAM DETECTED: {ai.get('spam_indicators', [])}")
        else:
            print(f"   ✅ Not spam")
    except:
        print(f"   ❌ Parse error")
    
    # Save to DB
    save_analysis(post_id, 'sonarpro', product['user_id'], {
        'relevance_score': row['relevance_score'],
        'semantic_similarity': row['semantic_similarity'],
        'community_score': 0,
        'ai_analysis': result,
        'signals_json': '{}',
        'last_processed_score': 0,
        'last_processed_comments': 0
    })
    
conn.close()
print("\n✅ Done! Check the UI for spam badges.")
