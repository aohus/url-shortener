from adapters.repository import SqlAlchemyRepository as repository
from domain.orm import Base, Session, engine
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from service_layer import services

Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()


# Dependency
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


class URLCreateRequest(BaseModel):
    url: HttpUrl


class URLCreateResponse(BaseModel):
    short_url: str


# Endpoint to create a shortened URL
@app.post("/shorten", response_model=URLCreateResponse)
def create_short_url(request: URLCreateRequest, session: Session = Depends(get_db)):
    repo = repository(session)
    # TODO: get? 이름 고민 get_or_create
    short_key = services.get_short_key(request.url, repo, session)
    short_url = f"http://url.shortener/{short_key}"
    return URLCreateResponse(short_url=short_url)


# Endpoint to redirect to the original URL
@app.get("/{short_key}")
def redirect_to_original(short_key: str, session: Session = Depends(get_db)):
    repo = repository(session)
    try:
        # TODO: service layer로
        original_url = repo.get(short_key=short_key)
    except:
        raise HTTPException(status_code=404, detail="URL not found")
    return RedirectResponse(original_url)
