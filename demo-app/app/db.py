"""Tiny sqlite helpers for the demo shop."""
import sqlite3

ALLOWED_TABLES = {"users", "items", "orders"}


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, pw_hash TEXT);
        CREATE TABLE IF NOT EXISTS items (
            sku TEXT PRIMARY KEY, name TEXT, qty INTEGER, price_cents INTEGER
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY, user_id INTEGER, total_cents INTEGER, status TEXT DEFAULT 'new'
        );
        """
    )
    return conn


def count_rows(conn, table):
    """Row count for one of the known tables."""
    if table not in ALLOWED_TABLES:
        raise ValueError(f"unknown table: {table}")
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def get_item(conn, sku):
    return conn.execute("SELECT * FROM items WHERE sku = ?", (sku,)).fetchone()


def add_item(conn, sku, name, qty, price_cents):
    conn.execute(
        "INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?)",
        (sku, name, qty, price_cents),
    )
    conn.commit()
