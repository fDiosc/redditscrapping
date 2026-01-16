"""Force AI reanalysis on top 30 posts and save results to file."""
from radar.storage.db import get_connection, save_analysis, get_product, get_comments
from radar.process.ai_analysis import analyze_post_with_ai
from radar.process.truncation import build_unified_context
import sqlite3
import json
from datetime import datetime

# Get product info
product = get_product('sonarpro')
if not product:
    print("Product not found")
    exit()

conn = get_connection()
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Find top 30 posts by relevance score
c.execute("""
    SELECT p.*, pa.relevance_score, pa.semantic_similarity
    FROM posts p
    JOIN post_analysis pa ON p.id = pa.post_id
    WHERE pa.product_id = 'sonarpro'
    ORDER BY pa.relevance_score DESC 
    LIMIT 200
""")
rows = c.fetchall()

print(f"🔄 Reanalyzing {len(rows)} posts with spam detection...\n")

results = []

for i, row in enumerate(rows, 1):
    post = dict(row)
    title_short = post['title'][:50] + "..." if len(post['title']) > 50 else post['title']
    print(f"[{i}/30] {title_short}")
    
    # Build context
    comments = get_comments(post['id'])
    unified = build_unified_context(post, comments)
    
    # Run AI analysis
    try:
        result = analyze_post_with_ai(unified, product)
        ai = json.loads(result)
        
        is_spam = ai.get('is_spam_or_ad', False)
        spam_indicators = ai.get('spam_indicators', [])
        
        status = "🚨 SPAM" if is_spam else "✅ OK"
        print(f"       {status}")
        
        results.append({
            'post_id': post['id'],
            'title': post['title'],
            'score': post['relevance_score'],
            'fit': post['semantic_similarity'],
            'is_spam_or_ad': is_spam,
            'spam_indicators': spam_indicators,
            'urgency': ai.get('urgency'),
            'pain_point_summary': ai.get('pain_point_summary'),
        })
        
        # Save to DB
        save_analysis(post['id'], 'sonarpro', product['user_id'], {
            'relevance_score': post['relevance_score'],
            'semantic_similarity': post['semantic_similarity'],
            'community_score': 0,
            'ai_analysis': result,
            'signals_json': '{}',
            'last_processed_score': post.get('score', 0),
            'last_processed_comments': post.get('num_comments', 0)
        })
        
    except Exception as e:
        print(f"       ❌ Error: {e}")
        results.append({
            'post_id': post['id'],
            'title': post['title'],
            'error': str(e)
        })

conn.close()

# Save results to file
output_file = f"spam_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Generate summary
spam_count = sum(1 for r in results if r.get('is_spam_or_ad'))
ok_count = sum(1 for r in results if r.get('is_spam_or_ad') == False)
error_count = sum(1 for r in results if 'error' in r)

print(f"\n{'='*50}")
print(f"📊 SUMMARY")
print(f"{'='*50}")
print(f"   🚨 Spam/AD detected: {spam_count}")
print(f"   ✅ Legitimate posts: {ok_count}")
print(f"   ❌ Errors: {error_count}")
print(f"\n📁 Results saved to: {output_file}")

# Print spam posts
if spam_count > 0:
    print(f"\n🚨 SPAM POSTS DETECTED:")
    for r in results:
        if r.get('is_spam_or_ad'):
            print(f"   • {r['title'][:60]}...")
            if r.get('spam_indicators'):
                for ind in r['spam_indicators'][:2]:
                    print(f"     - {ind}")
