from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

ResponseStyle = Literal["empathetic", "helpful_expert", "casual", "technical", "brief"]

class GenerateResponseRequest(BaseModel):
    """Request to generate a suggested response"""
    product_id: str
    style: ResponseStyle = "empathetic"

class GeneratedResponse(BaseModel):
    """Data object for a generated response"""
    id: str
    post_id: str
    product_id: str
    style: ResponseStyle
    response_text: str
    tokens_used: int
    created_at: datetime
    feedback: Optional[str] = None

class FeedbackRequest(BaseModel):
    """Request to update feedback for a response"""
    feedback: str # "good", "bad", "edited", "copied"
