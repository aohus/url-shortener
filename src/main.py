from datetime import datetime
from typing import Optional, Union

import config
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, HttpUrl, validator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from adapters import orm
from adapters.orm import metadata
from adapters.repository import SqlAlchemyRepository
from service_layer.services import URLNotExist, URLService

# Initialize logging
orm.start_mappers()

engine = create_engine(config.get_postgres_uri())
get_session = sessionmaker(bind=engine)
metadata.create_all(engine)

# Initialize FastAPI app
app = FastAPI(
    title="URL Shortener API",
    description="API for shortening URLs and tracking their usage.",
    version="1.0.0",
)


# Dependency to get DB session
def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


class URLCreateRequest(BaseModel):
    url: HttpUrl = Field(..., example="https://www.naver.com")
    expired_at: Optional[Union[datetime, str]] = Field(
        None, example="2024-06-30T05:47:41"
    )

    @validator("expired_at", pre=True, always=True)
    def parse_expired_at(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                try:
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        "Invalid date format. Use ISO 8601 or YYYY-MM-DD format."
                    )
        return v


class URLCreateResponse(BaseModel):
    short_url: str = Field(..., example="http://0.0.0.0:8000/abcd12")


class URLStatsResponse(BaseModel):
    short_key: str = Field(..., example="abcd12")
    views: int = Field(..., example=123)


def get_url_service(db: Session = Depends(get_db)) -> URLService:
    repo = SqlAlchemyRepository(db)
    return URLService(repo)


# Endpoint to create a shortened URL
@app.post(
    "/shorten",
    response_model=URLCreateResponse,
    summary="Create a shortened URL",
    description="Creates a new shortened URL with an optional expiration date.",
)
def create_short_url(
    request: URLCreateRequest, services: URLService = Depends(get_url_service)
):
    short_key = services.generate_short_key(request.url, request.expired_at)
    short_url = f"http://0.0.0.0:8000/{short_key}"
    return URLCreateResponse(short_url=short_url)


# Endpoint to redirect to the original URL
@app.get(
    "/{short_key}",
    summary="Redirect to original URL",
    description="Redirects to the original URL corresponding to the given short_key.",
)
def redirect_to_original(
    short_key: str, services: URLService = Depends(get_url_service)
):
    try:
        original_url = services.get_original_url(short_key)
    except URLNotExist as e:
        raise HTTPException(status_code=404, detail=str(e))
    return RedirectResponse(url=original_url, status_code=301)


@app.get(
    "/stats/{short_key}",
    response_model=URLStatsResponse,
    summary="Get URL stats",
    description="Returns the number of times the shortened URL has been accessed.",
)
async def get_stats(short_key: str, services: URLService = Depends(get_url_service)):
    try:
        views = services.get_view_count(short_key)
    except URLNotExist as e:
        raise HTTPException(status_code=404, detail=str(e))
    return URLStatsResponse(short_key=short_key, views=views)
