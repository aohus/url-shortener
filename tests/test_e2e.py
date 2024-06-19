# import pytest

# # app
# from adapters.orm import metadata
# from adapters.repository import SqlAlchemyRepository
# from domain import model
# from domain.model import URL
# from fastapi.testclient import TestClient
# from main import app
# from service_layer import services
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# # 테스트용 데이터베이스 설정
# DATABASE_URL_TEST = "sqlite:///./test_url_shortener.db"
# engine_test = create_engine(
#     DATABASE_URL_TEST,
#     connect_args={"check_same_thread": False},
# )


# # 테스트용 세션 생성
# get_test_session = sessionmaker(bind=engine_test)


# # 애플리케이션 인스턴스 생성
# client = TestClient(app)


# # 데이터베이스 초기화 함수
# @pytest.fixture(autouse=True)
# def setup_and_teardown():
#     metadata.create_all(engine_test)
#     yield
#     metadata.drop_all(engine_test)


# # 종속성 주입 함수 대체
# # app.dependency_overrides[get_session] = get_test_session


# # 단축 URL 생성 테스트
# def test_create_short_url():
#     response = client.post("/shorten", json={"url": "https://www.example.com"})
#     assert response.status_code == 200
#     data = response.json()
#     assert "short_url" in data
#     assert data["short_url"].startswith("http://0.0.0.0:8000/")


# # 기존 단축 URL 반환 테스트
# def test_return_existing_short_url():
#     session = get_test_session()
#     repo = SqlAlchemyRepository(session)
#     short_key = model.generate_short_url("https://www.example.com", repo)
#     response = client.post("/shorten", json={"url": "https://www.example.com"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["short_url"] == f"http://0.0.0.0:8000/{short_key}"


# # Repository의 get 메서드 테스트
# def test_repository_get():
#     session = get_test_session()
#     repo = SqlAlchemyRepository(session)
#     url = URL(original_url="https://www.example_1.com", short_key="abc123")
#     repo.add(url)
#     fetched_url = repo.get(short_key="abc123")
#     assert fetched_url is not None
#     assert fetched_url.original_url == "https://www.example_1.com"


# # Repository의 add 메서드 테스트
# def test_repository_add():
#     session = get_test_session()
#     repo = SqlAlchemyRepository(session)
#     url = URL(original_url="https://www.example_1.com", short_key="abc123")
#     added_url = repo.add(url)
#     assert added_url.id is not None
#     assert added_url.original_url == "https://www.example_1.com"
#     assert added_url.short_key == "abc123"
