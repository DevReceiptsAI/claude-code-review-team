import pytest

from app.db import add_item, connect


@pytest.fixture
def conn():
    c = connect()
    add_item(c, "A1", "Widget", 20, 1_000)
    add_item(c, "B2", "Gadget", 3, 2_500)
    add_item(c, "C3", "Gizmo", 50, 400)
    return c
