"""Shared fixtures: a small deterministic SQLite DB exercising users/orders/FKs."""
import csv
import sqlite3

import pytest


@pytest.fixture()
def db_path(tmp_path):
    """Path to a fresh fixture DB with 2 tables, an index, and an FK relationship."""
    p = tmp_path / "fixture.db"
    con = sqlite3.connect(str(p))
    try:
        cur = con.cursor()
        cur.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            );
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                amount REAL,
                created_at TEXT  -- ISO-8601 TEXT: SQLite has no native date type
            );
            INSERT INTO users VALUES (1, 'Ada', 'ada@example.com');
            INSERT INTO users VALUES (2, 'Alan', 'alan@example.com');
            INSERT INTO users VALUES (3, 'Grace', 'grace@example.com');
            INSERT INTO orders VALUES (10, 1, 9.5, '2026-01-01T00:00:00Z');
            INSERT INTO orders VALUES (11, 1, 4.0, '2026-01-02T00:00:00Z');
            INSERT INTO orders VALUES (12, 2, 7.25, '2026-01-03T00:00:00Z');
            INSERT INTO orders VALUES (13, 3, 15.0, '2026-02-01T00:00:00Z');
            """
        )
        cur.execute("CREATE INDEX idx_orders_user ON orders(user_id)")
        con.commit()
    finally:
        con.close()
    return str(p)


@pytest.fixture()
def sample_csv(tmp_path):
    """A CSV file for import tests (header + 3 rows)."""
    p = tmp_path / "import_me.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["code", "label"])
        w.writerow(["A1", "alpha"])
        w.writerow(["B2", "beta"])
        w.writerow(["C3", "gamma"])
    return str(p)
