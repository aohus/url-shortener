from datetime import datetime

from domain import model


def test_url_mapper_can_load_urls(session):
    session.execute(
        "INSERT INTO url (original_url, short_key, created_at, modified_at, expired_at, views) VALUES "
        '("https://www.example.com", "abcd12", "2024-01-01 00:00:00", "2024-01-01 00:00:00", "2025-01-01 00:00:00", 0),'
        '("https://www.anotherexample.com", "efgh34", "2024-02-01 00:00:00", "2024-02-01 00:00:00", "2024-12-31 00:00:00", 10),'
        '("https://www.thirdexample.com", "ijkl56", "2024-03-01 00:00:00", "2024-03-01 00:00:00", NULL, 5);'
    )
    expected = [
        model.URL(
            "https://www.example.com",
            "abcd12",
            datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"),
        ),
        model.URL(
            "https://www.anotherexample.com",
            "efgh34",
            datetime.strptime("2024-12-31 00:00:00", "%Y-%m-%d %H:%M:%S"),
        ),
        model.URL(
            "https://www.thirdexample.com",
            "ijkl56",
            None,
        ),
    ]
    assert session.query(model.URL).all() == expected


def test_url_mapper_can_save_url(session):
    expired_at = datetime.strptime("2024-06-30", "%Y-%m-%d")
    url = model.URL("https://www.example.com", "abcd12", expired_at)
    session.add(url)
    session.commit()

    rows = list(
        session.execute('SELECT original_url, short_key, expired_at FROM "url"')
    )
    assert rows == [
        (
            "https://www.example.com",
            "abcd12",
            expired_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
        )
    ]
