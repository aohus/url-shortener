# url-shortener
URL 단축 서비스는 긴 URL을 짧게 단축하여 사용하고, 단축된 URL을 통해 원본 URL로 리디렉션하는 기능을 제공합니다.


## Getting started

### Overview

Name    | Version
--------|---------
Python  | 3.9
FastAPI | 0.68.0
PostgreSQL | 9.6


### 프로젝트 설명

URL 단축 서비스는 긴 URL을 단축하여 저장하고, 해당 단축된 URL을 통해 원본 URL로 리디렉션하는 기능을 제공합니다. 이 프로젝트는 FastAPI를 사용하여 개발되었으며, 데이터베이스로는 PostgreSQL을 사용합니다.

### 프로젝트 기능

- 긴 URL을 단축 URL로 변환
    - 단축 URL의 유효 기간 설정 가능
- 단축 URL을 통한 원본 URL 리디렉션
- 단축 URL의 조회 수 추적

### API 문서
[`http://0.0.0.0:8000/docs`](http://0.0.0.0:8000/docs)에서 API 문서를 확인할 수 있습니다.


## Database
**PostgreSQL 9.6**
PostgreSQL은 ACID 준수, MVCC(Multi-Version Concurrency Control)를 통해 높은 동시성을 지원합니다. 
확장성과 애플리케이션의 특성, 관리의 용이성을 종합적으로 고려해서 가장 적절한 데이터베이스(들)를 선택하여야 하므로, 데이터 일관성과 무결성을 유지하면서도 여러 사용자가 동시에 URL을 단축하거나 조회할 때 성능 저하 없이 안정적인 서비스를 제공하기 위해 PostgreSQL을 선택했습니다. 


## Developer guide

애플리케이션 구동에 필요한 환경을 설정합니다.
- 필요 소프트웨어
    - Docker >= 24.0.6
    - Docker Compose >= 1.29.0

### 설치 및 실행 방법
1. 클론 및 디렉토리 이동
```bash
git clone https://github.com/your-repo/url-shortener.git
cd url-shortener
```

2. Docker 환경에서 실행
```bash
docker-compose up --build
```
FastAPI 서버는 기본적으로 [`http://0.0.0.0:8000`](http://0.0.0.0:8000)에서 실행됩니다.

3. 테스트 실행
```bash
bash test.sh
```


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
│   ├── conftest.py
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
├── wait-for-it.sh
```