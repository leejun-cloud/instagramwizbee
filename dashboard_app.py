from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import os
from pydantic import BaseModel

app = FastAPI(title="Wizbee Dashboard API")

DATA_FILE = "book_data.json"
SETTINGS_FILE = "settings.json"

# 마운트 정적 파일
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

class PostUpdate(BaseModel):
    hook: str
    caption: str
    hashtags: str
    approved: bool

class AutoModeSettings(BaseModel):
    auto_publish: bool

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"auto_publish": False}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("dashboard/templates/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/posts")
async def get_posts():
    return load_data()

@app.put("/api/posts/{day}")
async def update_post(day: int, post_update: PostUpdate):
    data = load_data()
    for post in data:
        if post.get("day") == day:
            post["hook"] = post_update.hook
            post["caption"] = post_update.caption
            post["hashtags"] = post_update.hashtags
            post["approved"] = post_update.approved
            save_data(data)
            return {"message": "Success", "post": post}
    raise HTTPException(status_code=404, detail="Post not found")

@app.delete("/api/posts/{day}")
async def delete_post(day: int):
    data = load_data()
    new_data = [p for p in data if p.get("day") != day]
    if len(data) == len(new_data):
        raise HTTPException(status_code=404, detail="Post not found")
    save_data(new_data)
    return {"message": "Deleted"}

@app.get("/api/settings")
async def get_settings():
    return load_settings()

@app.post("/api/settings")
async def update_settings(settings: AutoModeSettings):
    save_settings(settings.dict())
    return {"message": "Settings updated"}

# Run Command: uvicorn main:app --reload
