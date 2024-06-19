from domain import model
from sqlalchemy import Column, Date, Integer, MetaData, String, Table
from sqlalchemy.orm import mapper

metadata = MetaData()

url = Table(
    "url",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("original_url", String, index=True),
    Column("short_key", String, index=True),
    # Column("create_at", Date),
)


def start_mappers():
    mapper(
        model.URL,
        url,
    )
