import pytest
from radar.storage.db import (
    save_post, 
    save_analysis, 
    get_unprocessed_posts, 
    get_sync_history, 
    add_sync_run
)

def test_user_data_isolation(db_conn):
    # 1. Setup - Create a post
    post_data = {
        'id': 'test_post_1',
        'platform': 'reddit',
        'source': 'test_sub',
        'title': 'Test Title',
        'score': 100,
        'num_comments': 10,
        'ingestion_method': 'scraper'
    }
    save_post(post_data)
    
    # Manually set embedding_id in SQL to simulate global processing
    from radar.storage.db import get_connection
    conn = get_connection()
    conn.execute("UPDATE posts SET embedding_id = ? WHERE id = ?", ("emb_123", "test_post_1"))
    conn.commit()
    conn.close()

    # 2. Analyze for User A
    save_analysis('test_post_1', 'product_a', 'user_a', {
        'relevance_score': 15.0,
        'semantic_similarity': 0.8,
        'last_processed_score': 100,
        'last_processed_comments': 10
    })

    # 3. Analyze for User B (Different result)
    save_analysis('test_post_1', 'product_b', 'user_b', {
        'relevance_score': 5.0,
        'semantic_similarity': 0.2,
        'last_processed_score': 100,
        'last_processed_comments': 10
    })

    # 4. Verify isolation in unprocessed posts
    # For User A, product_a: post is processed (0 pending)
    pending_a = get_unprocessed_posts(user_id='user_a', product_id='product_a')
    assert len(pending_a) == 0

    # For User C (New user), product_c: post is NOT processed (1 pending)
    pending_c = get_unprocessed_posts(user_id='user_c', product_id='product_c')
    assert len(pending_c) == 1
    assert pending_c[0]['id'] == 'test_post_1'

def test_sync_history_isolation(db_conn):
    # Add runs for different users
    add_sync_run('user_felipe', 'prod1', ['sub1'], 7)
    add_sync_run('user_joao', 'prod2', ['sub2'], 3)

    # Check Felipe's history
    history_felipe = get_sync_history('user_felipe')
    assert len(history_felipe) == 1
    assert history_felipe[0]['user_id'] == 'user_felipe'

    # Check Joao's history
    history_joao = get_sync_history('user_joao')
    assert len(history_joao) == 1
    assert history_joao[0]['user_id'] == 'user_joao'
