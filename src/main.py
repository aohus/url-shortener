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

DATABASE_URL = "sqlite:///./url_shortener.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

get_session = sessionmaker(bind=engine)
metadata.create_all(engine)
# get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

# Initialize FastAPI app
app = FastAPI()


class URLCreateRequest(BaseModel):
    url: HttpUrl


class URLCreateResponse(BaseModel):
    short_url: str


# Endpoint to create a shortened URL
@app.post("/shorten", response_model=URLCreateResponse)
def create_short_url(request: URLCreateRequest):
    session = get_session()
    repo = SqlAlchemyRepository(session)
    # TODO: get? 이름 고민 get_or_create
    short_key = services.get_short_key(request.url, repo)
    short_url = f"http://0.0.0.0:8000/{short_key}"
    return URLCreateResponse(short_url=short_url)


# Endpoint to redirect to the original URL
@app.get("/{short_key}")
def redirect_to_original(short_key: str):
    session = get_session()
    repo = SqlAlchemyRepository(session)
    try:
        # TODO: service layer로
        original_url = repo.get(short_key=short_key).original_url
    except:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(url=original_url, status_code=302)
