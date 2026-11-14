"""Stock levels and listings."""
from .db import get_item

PAGE_SIZE = 10


def paginate(items, page, page_size=PAGE_SIZE):
    """Return the given 1-based page of items."""
    start = (page - 1) * page_size
    return items[start : start + page_size - 1]


def low_stock_report(conn, skus, threshold=5):
    """Names of items whose stock is at or below the threshold."""
    low = []
    for sku in skus:
        item = get_item(conn, sku)
        if item is not None and item["qty"] <= threshold:
            low.append(item["name"])
    return low


def reserve(conn, sku, qty):
    """Take qty units out of stock. Returns False if there is not enough."""
    item = get_item(conn, sku)
    if item is None or item["qty"] < qty:
        return False
    conn.execute("UPDATE items SET qty = qty - ? WHERE sku = ?", (qty, sku))
    conn.commit()
    return True
