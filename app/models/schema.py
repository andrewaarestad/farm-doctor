from pydantic import BaseModel, Field
from typing import Optional, List

class LLMRequest(BaseModel):
    prompt: str = Field(..., description="The input prompt for the LLM")
    model: str = Field(default="gpt-3.5-turbo", description="The LLM model to use")
    max_tokens: Optional[int] = Field(default=100, description="Maximum tokens in response")
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Sampling temperature"
    )

class LLMResponse(BaseModel):
    text: str = Field(..., description="The generated text response")
    model: str = Field(..., description="The model used for generation")
    tokens_used: int = Field(..., description="Number of tokens used in response")

    class Config:
        schema_extra = {
            "example": {
                "text": "This is a sample response",
                "model": "gpt-3.5-turbo",
                "tokens_used": 5
            }
        }
