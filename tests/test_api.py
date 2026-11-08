from fastapi.testclient import TestClient

from tests.conftest import DUNE, HEADERS

ISBN = "9780441172719"


def test_health_reports_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_add_book_requires_api_key(client: TestClient) -> None:
    assert client.post("/books", json=DUNE).status_code == 401


def test_add_book_rejects_wrong_api_key(client: TestClient) -> None:
    response = client.post("/books", json=DUNE, headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_add_and_fetch_book(client: TestClient) -> None:
    created = client.post("/books", json=DUNE, headers=HEADERS)
    assert created.status_code == 201
    assert created.json()["isbn"] == ISBN

    fetched = client.get(f"/books/{ISBN}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Dune"


def test_duplicate_book_is_a_conflict(client: TestClient) -> None:
    client.post("/books", json=DUNE, headers=HEADERS)
    assert client.post("/books", json=DUNE, headers=HEADERS).status_code == 409


def test_invalid_isbn_is_rejected(client: TestClient) -> None:
    bad = {**DUNE, "isbn": "978-0-441-17271-0"}
    assert client.post("/books", json=bad, headers=HEADERS).status_code == 422


def test_unknown_book_is_not_found(client: TestClient) -> None:
    assert client.get(f"/books/{ISBN}").status_code == 404


def test_search_matches_title_and_author(client: TestClient) -> None:
    client.post("/books", json=DUNE, headers=HEADERS)
    assert len(client.get("/books", params={"q": "dun"}).json()) == 1
    assert len(client.get("/books", params={"q": "Herbert"}).json()) == 1
    assert client.get("/books", params={"q": "tolkien"}).json() == []


def test_search_treats_wildcards_literally(client: TestClient) -> None:
    client.post("/books", json=DUNE, headers=HEADERS)
    assert client.get("/books", params={"q": "%"}).json() == []


def test_stock_can_go_down_but_not_below_zero(client: TestClient) -> None:
    client.post("/books", json=DUNE, headers=HEADERS)
    url = f"/books/{ISBN}/stock"

    sold = client.patch(url, json={"change": -2}, headers=HEADERS)
    assert sold.json()["stock"] == 1

    oversold = client.patch(url, json={"change": -5}, headers=HEADERS)
    assert oversold.status_code == 409


def test_stock_change_for_unknown_book(client: TestClient) -> None:
    url = f"/books/{ISBN}/stock"
    response = client.patch(url, json={"change": 1}, headers=HEADERS)
    assert response.status_code == 404
