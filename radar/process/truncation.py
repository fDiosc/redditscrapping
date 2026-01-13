import tiktoken
from typing import List, Dict, Any

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Returns the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def build_unified_context(post: Dict[str, Any], comments: List[Dict[str, Any]], max_tokens: int = 7500) -> str:
    """
    Builds a unified context string while respecting token limits.
    Priority: Title > Body > Top Comments (sorted by score).
    """
    title = post.get('title', '')
    body = post.get('body', '')
    
    # 1. Reserve space for Title and basic structure
    header = f"TITLE: {title}\nAUTHOR: {post.get('author', 'unknown')}\n"
    body_header = "BODY: "
    comments_header = "\n\nCOMMUNITY COMMENTS:\n"
    
    # If title alone is too crazy (very unlikely)
    if count_tokens(header + body_header + comments_header) > max_tokens:
        return header[:max_tokens * 3] # Emergency fallback
        
    current_tokens = count_tokens(header + body_header + comments_header)
    
    # 2. Add Body (Truncate if necessary)
    body_tokens = count_tokens(body)
    if current_tokens + body_tokens > max_tokens - 1000: # Reserve 1000 for comments
        # Truncate body to fit
        remaining_for_body = max_tokens - current_tokens - 1000
        # Rough truncation (characters are ~4 per token)
        body = body[:remaining_for_body * 3] + "... [Post body truncated]"
        body_tokens = count_tokens(body)
        
    current_text = header + body_header + body + comments_header
    current_tokens += body_tokens
    
    # 3. Add Comments (Sorted by score)
    comments_included = 0
    for cmd in comments:
        cmd_text = f"COMMENT BY u/{cmd.get('author', 'unknown')}: {cmd['body']}\n"
        cmd_tokens = count_tokens(cmd_text)
        
        if current_tokens + cmd_tokens > max_tokens:
            break
            
        current_text += cmd_text
        current_tokens += cmd_tokens
        comments_included += 1
        
    # print(f"DEBUG: Context for '{post['id']}' built with {current_tokens} tokens and {comments_included}/{len(comments)} comments.")
    return current_text
