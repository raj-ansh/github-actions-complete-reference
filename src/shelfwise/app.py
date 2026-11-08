"""HTTP API for ShelfWise."""

import logging
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from shelfwise import __version__
from shelfwise.isbn import InvalidISBN, normalise
from shelfwise.repository import (
    Book,
    BookNotFound,
    BookRepository,
    DuplicateBook,
    InsufficientStock,
)
from shelfwise.settings import Settings, load_settings

logger = logging.getLogger("shelfwise")


class NewBook(BaseModel):
    isbn: str = Field(min_length=10, max_length=20)
    title: str = Field(min_length=1, max_length=300)
    author: str = Field(min_length=1, max_length=200)
    stock: int = Field(ge=0, default=0)


class StockChange(BaseModel):
    change: int = Field(ge=-10_000, le=10_000)


class BookOut(BaseModel):
    isbn: str
    title: str
    author: str
    stock: int


def to_output(book: Book) -> BookOut:
    return BookOut(
        isbn=book.isbn, title=book.title, author=book.author, stock=book.stock
    )


def parse_isbn(raw: str) -> str:
    try:
        return normalise(raw)
    except InvalidISBN as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)
        ) from error


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or load_settings()
    repository = BookRepository(config.database_path)
    app = FastAPI(title="ShelfWise", version=__version__)

    def require_api_key(
        x_api_key: Annotated[str, Header()] = "",
    ) -> None:
        if not secrets.compare_digest(x_api_key, config.api_key):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid API key")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/books")
    def search_books(
        q: Annotated[str, Query(max_length=100)] = "",
    ) -> list[BookOut]:
        return [to_output(book) for book in repository.search(q)]

    @app.get("/books/{isbn}")
    def get_book(isbn: str) -> BookOut:
        try:
            return to_output(repository.get(parse_isbn(isbn)))
        except BookNotFound as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such book") from error

    @app.post(
        "/books",
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_api_key)],
    )
    def add_book(new_book: NewBook) -> BookOut:
        book = Book(
            parse_isbn(new_book.isbn), new_book.title, new_book.author, new_book.stock
        )
        try:
            repository.add(book)
        except DuplicateBook as error:
            raise HTTPException(status.HTTP_409_CONFLICT, "book exists") from error
        logger.info("added book %s", book.isbn)
        return to_output(book)

    @app.patch("/books/{isbn}/stock", dependencies=[Depends(require_api_key)])
    def change_stock(isbn: str, body: StockChange) -> BookOut:
        try:
            return to_output(repository.adjust_stock(parse_isbn(isbn), body.change))
        except BookNotFound as error:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "no such book") from error
        except InsufficientStock as error:
            raise HTTPException(status.HTTP_409_CONFLICT, "not enough stock") from error

    return app
