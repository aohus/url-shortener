from datetime import datetime
from typing import Optional

import config
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from adapters import orm
from adapters.orm import metadata
from adapters.repository import SqlAlchemyRepository
from service_layer import services

# Initialize logging
orm.start_mappers()

engine = create_engine(config.get_postgres_uri())
get_session = sessionmaker(bind=engine)
metadata.create_all(engine)

# Initialize FastAPI app
app = FastAPI()


class URLCreateRequest(BaseModel):
    url: HttpUrl
    expired_at: Optional[datetime] = None


class URLCreateResponse(BaseModel):
    short_url: str


# Endpoint to create a shortened URL
@app.post("/shorten", response_model=URLCreateResponse)
def create_short_url(request: URLCreateRequest):
    session = get_session()
    repo = SqlAlchemyRepository(session)
    short_key = services.generate_short_key(request.url, request.expired_at, repo)
    short_url = f"http://0.0.0.0:8000/{short_key}"
    return URLCreateResponse(short_url=short_url)


# Endpoint to redirect to the original URL
@app.get("/{short_key}")
def redirect_to_original(short_key: str):
    session = get_session()
    repo = SqlAlchemyRepository(session)
    try:
        original_url = services.get_original_url(short_key, repo)
    except services.URLNotExist as e:
        raise HTTPException(status_code=404, detail=str(e))
    return RedirectResponse(url=original_url, status_code=301)
