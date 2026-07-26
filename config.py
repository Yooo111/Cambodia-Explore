import os
import socket
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

def is_mysql_available(host="127.0.0.1", port=3306):
    """Quickly check if MySQL server is accepting connections."""
    try:
        sock = socket.create_connection((host, port), timeout=0.5)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key")

    # If DATABASE_URL is set in env, use it. Otherwise, check if MySQL is running on port 3306.
    default_sqlite_path = os.path.join(BASE_DIR, 'instance', 'urac_db.db')
    os.makedirs(os.path.dirname(default_sqlite_path), exist_ok=True)
    default_sqlite_uri = f"sqlite:///{os.path.abspath(default_sqlite_path)}"

    if os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    elif is_mysql_available():
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/urac_db?charset=utf8mb4"
    else:
        SQLALCHEMY_DATABASE_URI = default_sqlite_uri

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


