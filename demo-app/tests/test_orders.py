from app.orders import (
    apply_discount,
    count_by_status,
    dedupe_skus,
    format_price,
    order_total,
    place_order,
)


def test_no_discount_below_threshold():
    assert apply_discount(5_000) == 5_000


def test_discount_on_large_order():
    assert apply_discount(20_000) == 18_000


def test_discount_at_threshold():
    result = apply_discount(10_000)
    print(result)


def test_order_total_without_discount():
    assert order_total([(1_000, 2)]) == 2_160


def test_dedupe_keeps_first_seen_order():
    assert dedupe_skus(["a", "b", "a", "c", "b"]) == ["a", "b", "c"]


def test_count_by_status():
    orders = [{"status": "new"}, {"status": "paid"}, {"status": "new"}]
    assert count_by_status(orders) == {"new": 2, "paid": 1, "shipped": 0, "cancelled": 0}


def test_format_price():
    assert format_price(1999) == "$19.99"
    assert format_price(-150) == "-$1.50"


def test_place_order_reserves_stock(conn):
    order_id = place_order(conn, 1, [("A1", 2)])
    assert order_id is not None
    assert conn.execute("SELECT qty FROM items WHERE sku='A1'").fetchone()[0] == 18


def test_place_order_fails_when_out_of_stock(conn):
    assert place_order(conn, 1, [("A1", 2), ("B2", 99)]) is None
    assert conn.execute("SELECT qty FROM items WHERE sku='A1'").fetchone()[0] == 20
