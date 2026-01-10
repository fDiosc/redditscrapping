import openai
from typing import Dict, Any
from radar.config import OPENAI_API_KEY
from radar.products import PRODUCTS

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def analyze_post_with_ai(post_data: Dict[str, Any], product_key: str) -> str:
    product = PRODUCTS.get(product_key)
    if not product:
        return "Product not found in knowledge base."
        
    prompt = f"""
    Analyze the following Reddit post and determine how it relates to the product "{product['name']}".
    
    Product Description: {product['description']}
    Target Audience: {product['target_audience']}
    Key Features: {', '.join(product['key_features'])}
    
    Reddit Post Title: {post_data['title']}
    Reddit Post Body: {post_data['body']}
    
    Please provide:
    1. A brief assessment of the user's pain point.
    2. How the product could potentially solve this specific problem.
    3. A 'fit' rating from 1-10.
    
    Keep the response concise and in Markdown format.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a product analyst helping a founder find leads and insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis failed: {e}"
