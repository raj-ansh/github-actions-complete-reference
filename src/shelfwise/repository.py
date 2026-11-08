"""SQLite storage for the book inventory."""

import sqlite3
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    isbn   TEXT PRIMARY KEY,
    title  TEXT NOT NULL,
    author TEXT NOT NULL,
    stock  INTEGER NOT NULL CHECK (stock >= 0)
)
"""


@dataclass(frozen=True)
class Book:
    isbn: str
    title: str
    author: str
    stock: int


class DuplicateBook(Exception):
    """Raised when a book with the same ISBN already exists."""


class BookNotFound(Exception):
    """Raised when no book has the requested ISBN."""


class InsufficientStock(Exception):
    """Raised when a change would make stock negative."""


class BookRepository:
    def __init__(self, database_path: str) -> None:
        self._connection = sqlite3.connect(database_path, check_same_thread=False)
        self._connection.execute(SCHEMA)
        self._connection.commit()

    def add(self, book: Book) -> None:
        try:
            with self._connection:
                self._connection.execute(
                    "INSERT INTO books (isbn, title, author, stock) "
                    "VALUES (?, ?, ?, ?)",
                    (book.isbn, book.title, book.author, book.stock),
                )
        except sqlite3.IntegrityError as error:
            raise DuplicateBook(book.isbn) from error

    def get(self, isbn: str) -> Book:
        row = self._connection.execute(
            "SELECT isbn, title, author, stock FROM books WHERE isbn = ?", (isbn,)
        ).fetchone()
        if row is None:
            raise BookNotFound(isbn)
        return Book(*row)

    def search(self, term: str) -> list[Book]:
        escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{escaped}%"
        rows = self._connection.execute(
            "SELECT isbn, title, author, stock FROM books "
            "WHERE title LIKE ? ESCAPE '\\' OR author LIKE ? ESCAPE '\\' "
            "ORDER BY title",
            (pattern, pattern),
        ).fetchall()
        return [Book(*row) for row in rows]

    def adjust_stock(self, isbn: str, change: int) -> Book:
        book = self.get(isbn)
        new_stock = book.stock + change
        if new_stock < 0:
            raise InsufficientStock(isbn)
        with self._connection:
            self._connection.execute(
                "UPDATE books SET stock = ? WHERE isbn = ?", (new_stock, isbn)
            )
        return Book(book.isbn, book.title, book.author, new_stock)
