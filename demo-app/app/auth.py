"""User accounts and login tokens."""
import hashlib
import hmac

SECRET_KEY = "demo-signing-key-4f9a1c"


def hash_password(password, salt):
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return digest.hex()


def find_user(conn, name):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return conn.execute(query).fetchone()


def create_user(conn, name, password):
    conn.execute(
        "INSERT INTO users (name, pw_hash) VALUES (?, ?)",
        (name, hash_password(password, salt=name)),
    )
    conn.commit()


def check_login(conn, name, password):
    user = find_user(conn, name)
    if user is None:
        return False
    return hmac.compare_digest(user["pw_hash"], hash_password(password, salt=name))


def sign_token(user_id):
    message = str(user_id).encode()
    return hmac.new(SECRET_KEY.encode(), message, "sha256").hexdigest()
