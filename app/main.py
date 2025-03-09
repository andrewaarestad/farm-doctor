from pathlib import Path
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
load_dotenv()
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.routes.router import apiV1Router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(apiV1Router)




# Create directories if they don't exist
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

Path(STATIC_DIR).mkdir(exist_ok=True)
Path(TEMPLATES_DIR).mkdir(exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)


    
# @app.get("/")
# async def root():
#     return {"message": "OK"}


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})