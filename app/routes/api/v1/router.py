from fastapi import APIRouter, HTTPException
from app.models.schema import LLMRequest, LLMResponse

apiV1Router = APIRouter(prefix="/api/v1")

@apiV1Router.post("/llm", response_model=LLMResponse)
async def query_llm(request: LLMRequest):
    try:
        # This is where you'd typically make a call to your LLM API
        # For example: OpenAI, Anthropic, etc.
        response = f"Processed prompt: {request.prompt}"
        return LLMResponse(
            text=response,
            model=request.model,
            tokens_used=len(response.split())
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
