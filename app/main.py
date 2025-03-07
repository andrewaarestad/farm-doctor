from fastapi import FastAPI
from app.core.config import settings
from app.routes.router import apiV1Router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(apiV1Router)
    
@app.get("/")
async def root():
    return {"message": "OK"}
