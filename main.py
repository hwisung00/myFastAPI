from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import shortuuid

import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/shorten")
async def shorten_url(request: Request, long_url: str = Form(...), db: Session = Depends(get_db)):
    key = shortuuid.uuid()
    db_url = models.URL(key=key, long_url=long_url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    short_url = f"{request.base_url}{key}"
    return templates.TemplateResponse("index.html", {"request": request, "short_url": short_url})

@app.get("/{key}")
async def redirect_to_long_url(key: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URL).filter(models.URL.key == key).first()
    if db_url:
        return RedirectResponse(url=db_url.long_url)
    return templates.TemplateResponse("index.html", {"request": request, "error": "URL not found"})