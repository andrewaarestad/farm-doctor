from fastapi import APIRouter
from app.routes.api.v1.llm.post import LLMRouter

apiV1Router = APIRouter(prefix="/api/v1")

apiV1Router.include_router(LLMRouter)
