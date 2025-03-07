from typing import Union
from fastapi import FastAPI
from app.routes.api.v1.router import apiV1Router
from app.core.config import settings
from app.models.Item import Item

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(apiV1Router)
    
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}