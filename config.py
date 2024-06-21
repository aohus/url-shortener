import os


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 5432
    password = os.environ.get("DB_PASSWORD", "password")
    user = "postgres"
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/"
