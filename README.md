# url-shortener
URL 단축 서비스는 긴 URL을 짧게 단축하여 사용하고, 단축된 URL을 통해 원본 URL로 리디렉션하는 기능을 제공합니다.


## Getting started

### Overview

Name    | Version
--------|---------
Python  | 3.11
FastAPI | 0.68.0
PostgreSQL | 9.6
Redis | 0.0

## Developer guide

애플리케이션 구동에 필요한 환경을 설정합니다.
- 필요 소프트웨어
    - Docker >= 24.0.6

### Docker build & FastAPI 실행
docker-compose 명령으로 FastAPI 앱을 시작합니다. 
```bash
docker-compose up
```

### 테스트 실행
```bash
bash test.sh
```

## Database

## 디렉토리 구조
```
url-shortener/
├── src/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── orm.py
│   │   ├── repository.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── model.py
│   ├── service_layer/
│   │   ├── __init__.py
│   │   ├── services.py
│   ├── main.py
├── tests/
│   ├── __pycache__/
│   ├── conf_test.py
│   ├── test_e2e.py
│   ├── test_generate_key.py
│   ├── test_orm.py
│   ├── test_repository.py
│   ├── test_services.py
├── .env
├── .gitignore
├── config.py
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.test
├── poetry.lock
├── pyproject.toml
├── test.sh
```