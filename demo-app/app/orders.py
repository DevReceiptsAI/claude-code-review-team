"""Pricing and order placement. All money is integer cents."""
from .db import get_item
from .inventory import reserve

DISCOUNT_THRESHOLD_CENTS = 10_000
DISCOUNT_RATE_PERCENT = 10
TAX_RATE_PERCENT = 8
STATUSES = ("new", "paid", "shipped", "cancelled")


def apply_discount(subtotal_cents):
    """Orders of $100.00 or more get 10% off."""
    if subtotal_cents > DISCOUNT_THRESHOLD_CENTS:
        return subtotal_cents - subtotal_cents * DISCOUNT_RATE_PERCENT // 100
    return subtotal_cents


def order_total(lines):
    """Total in cents. Discount applies to the subtotal, then tax is charged
    on the discounted amount. lines is a list of (price_cents, qty)."""
    subtotal = sum(price * qty for price, qty in lines)
    discounted = apply_discount(subtotal)
    tax = subtotal * TAX_RATE_PERCENT // 100
    return discounted + tax


def format_price(cents):
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}${cents // 100}.{cents % 100:02d}"


def dedupe_skus(skus):
    """Remove duplicate SKUs, keeping first-seen order."""
    seen = []
    for sku in skus:
        if sku not in seen:
            seen.append(sku)
    return seen


def count_by_status(orders):
    counts = {}
    for status in STATUSES:
        counts[status] = 0
        for order in orders:
            if order["status"] == status:
                counts[status] += 1
    return counts


def place_order(conn, user_id, cart):
    """cart is a list of (sku, qty). Returns the order id, or None if any line
    cannot be filled (nothing is reserved in that case)."""
    priced = []
    for sku, qty in cart:
        item = get_item(conn, sku)
        if item is None or item["qty"] < qty:
            return None
        priced.append((sku, qty, item["price_cents"]))
    for sku, qty, _ in priced:
        reserve(conn, sku, qty)
    total = order_total([(price, qty) for _, qty, price in priced])
    cur = conn.execute(
        "INSERT INTO orders (user_id, total_cents) VALUES (?, ?)", (user_id, total)
    )
    conn.commit()
    return cur.lastrowid
