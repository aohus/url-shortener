from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./url_shortener.db"
engine = create_engine(
    # connect_args={"check_same_thread": False} for sqlite
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
