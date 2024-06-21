from domain import model
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, event, func
from sqlalchemy.orm import mapper

metadata = MetaData()

url = Table(
    "url",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("original_url", String, index=True, nullable=False),
    Column("short_key", String, index=True, nullable=False),
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column(
        "modified_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False
    ),
    Column("expired_at", DateTime, nullable=True),
    Column("views", Integer, default=0, nullable=False),
)


def start_mappers():
    mapper(model.URL, url)

    @event.listens_for(model.URL, "before_update")
    def receive_before_update(mapper, connection, target):
        target.update_modified_at()
