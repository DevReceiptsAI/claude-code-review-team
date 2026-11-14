"""Report export and download helpers."""
import os

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "exports")


def export_report(filename, text):
    """Write a report into the exports folder and return its path."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, filename)
    with open(path, "w") as f:
        f.write(text)
    return path


def read_report(filename):
    """Read a report back from the exports folder."""
    path = os.path.join(EXPORT_DIR, os.path.basename(filename))
    with open(path) as f:
        return f.read()
