from app import files
from app.auth import check_login, create_user, find_user, sign_token


def test_login_success_and_failure(conn):
    create_user(conn, "ada", "correct horse")
    assert check_login(conn, "ada", "correct horse") is True
    assert check_login(conn, "ada", "wrong") is False
    assert check_login(conn, "nobody", "x") is False


def test_find_user(conn):
    create_user(conn, "ada", "pw")
    assert find_user(conn, "ada")["name"] == "ada"


def test_sign_token_is_stable():
    assert sign_token(7) == sign_token(7)
    assert sign_token(7) != sign_token(8)


def test_export_and_read_report(tmp_path, monkeypatch):
    monkeypatch.setattr(files, "EXPORT_DIR", str(tmp_path))
    files.export_report("q1.txt", "hello")
    assert files.read_report("q1.txt") == "hello"
