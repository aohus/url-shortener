from pydantic import HttpUrl
from sqlmodel import Field, SQLModel


# URL model
class URL(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    original_url: HttpUrl
    short_key: str
