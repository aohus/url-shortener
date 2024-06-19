from adapters.orm import Base
from sqlalchemy import Column, Integer, String


# URL model
class URL(Base):
    __tablename__ = "url"

    id: int = Column(Integer, primary_key=True)
    original_url: str = Column(String, index=True)
    short_key: str = Column(String, index=True)
