from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import sessionmaker

from .orm import engine, init_db
from .repository import SqlAlchemyRepository as repository
from .service import generate_short_key

# Initialize FastAPI app
app = FastAPI()


class URLCreateRequest(BaseModel):
    url: HttpUrl


class URLCreateResponse(BaseModel):
    short_url: str


get_session = sessionmaker(engine)


@app.on_event("startup")
def on_startup():
    init_db()


# Endpoint to create a shortened URL
@app.post("/shorten", response_model=URLCreateResponse)
def create_short_url(request: URLCreateRequest):
    session = get_session()
    repo = repository(session)
    original_url = request.url

    short_key = repo.get(original_url=original_url)
    if short_key:
        return URLCreateResponse(short_url=f"http://localhost:8000/{short_key}")

    short_key = generate_short_key()
    short_url = f"http://localhost:8000/{short_key}"
    return URLCreateResponse(short_url=short_url)


# Endpoint to redirect to the original URL
@app.get("/{short_key}")
def redirect_to_original(short_key: str):
    session = get_session()
    repo = repository(session)
    try:
        short_key = repo.get(short_key=short_key)
    except:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(short_key)
