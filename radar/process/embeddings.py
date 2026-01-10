import openai
from typing import List
from radar.config import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_embeddings(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    # Simple cleanup to remove empty or too short strings
    cleaned_texts = [text.replace("\n", " ") for text in texts]
    
    response = client.embeddings.create(
        input=cleaned_texts,
        model=model
    )
    
    return [data.embedding for data in response.data]
