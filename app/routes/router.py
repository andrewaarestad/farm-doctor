from fastapi import APIRouter
from app.routes.api.v1.chat.langgraph.post import langgraph_router
from app.routes.api.v1.chat.openai.post import openai_router

apiV1Router = APIRouter(prefix="/api/v1")

apiV1Router.include_router(langgraph_router)
apiV1Router.include_router(openai_router)
