import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from .main import app, get_session
from .model import URL
from .orm import init_db
from .repository import URLRepository
from .service import URLService

# 테스트용 데이터베이스 설정
DATABASE_URL_TEST = "sqlite:///./test_url_shortener.db"
engine_test = create_engine(DATABASE_URL_TEST)


# 테스트용 세션 생성
def get_test_session():
    with Session(engine_test) as session:
        yield session


# 애플리케이션 인스턴스 생성
client = TestClient(app)


# 데이터베이스 초기화 함수
@pytest.fixture(autouse=True)
def setup_and_teardown():
    SQLModel.metadata.create_all(engine_test)
    yield
    SQLModel.metadata.drop_all(engine_test)


# 종속성 주입 함수 대체
app.dependency_overrides[get_session] = get_test_session


# 단축 URL 생성 테스트
def test_create_short_url():
    response = client.post("/shorten", json={"url": "https://www.example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["short_url"].startswith("http://localhost:8000/")


# 기존 단축 URL 반환 테스트
def test_return_existing_short_url():
    session = next(get_test_session())
    service = URLService(session)
    short_key = service.create_short_url("https://www.example.com")
    response = client.post("/shorten", json={"url": "https://www.example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["short_url"] == f"http://localhost:8000/{short_key}"


# Repository의 get_by_key 메서드 테스트
def test_repository_get_by_key():
    session = next(get_test_session())
    repo = URLRepository(session)
    url = URL(original_url="https://www.example.com", short_key="abc123")
    repo.add(url)
    fetched_url = repo.get_by_key("short_key", "abc123")
    assert fetched_url is not None
    assert fetched_url.original_url == "https://www.example.com"


# Repository의 add 메서드 테스트
def test_repository_add():
    session = next(get_test_session())
    repo = URLRepository(session)
    url = URL(original_url="https://www.example.com", short_key="abc123")
    added_url = repo.add(url)
    assert added_url.id is not None
    assert added_url.original_url == "https://www.example.com"
    assert added_url.short_key == "abc123"


# Service의 get 메서드 테스트
def test_service_get():
    session = next(get_test_session())
    service = URLService(session)
    url = URL(original_url="https://www.example.com", short_key="abc123")
    service.repo.add(url)
    fetched_url = service.get(short_key="abc123")
    assert fetched_url is not None
    assert fetched_url.original_url == "https://www.example.com"


# Service의 create_short_url 메서드 테스트
def test_service_create_short_url():
    session = next(get_test_session())
    service = URLService(session)
    short_key = service.create_short_url("https://www.example.com")
    assert len(short_key) == 6
    fetched_url = service.get(short_key=short_key)
    assert fetched_url is not None
    assert fetched_url.original_url == "https://www.example.com"
