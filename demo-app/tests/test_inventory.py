from app.db import count_rows
from app.inventory import low_stock_report, paginate, reserve


def test_paginate_respects_page_size():
    page = paginate(list(range(25)), 1, page_size=10)
    assert len(page) <= 10


def test_paginate_last_page():
    assert paginate(list(range(25)), 3, page_size=10) == [20, 21, 22, 23, 24]


def test_low_stock_report(conn):
    assert low_stock_report(conn, ["A1", "B2", "C3"]) == ["Gadget"]


def test_reserve_success_and_failure(conn):
    assert reserve(conn, "B2", 2) is True
    assert reserve(conn, "B2", 2) is False


def test_count_rows(conn):
    assert count_rows(conn, "items") == 3
