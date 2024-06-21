from datetime import datetime

from adapters import repository
from domain import model


def test_repository_can_save_a_url(session):
    expired_at = datetime.strptime("2024-06-30", "%Y-%m-%d")
    url = model.URL(
        original_url="https://www.example.com",
        short_key="XYZ123",
        expired_at=expired_at,
    )

    repo = repository.SqlAlchemyRepository(session)
    repo.add(url)
    session.commit()

    rows = session.execute('SELECT original_url, short_key, expired_at FROM "url"')
    assert list(rows) == [
        (
            "https://www.example.com",
            "XYZ123",
            expired_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
        )
    ]
