import os

from dotenv import load_dotenv

load_dotenv()


def config():
    """
    Получение параметров подключения к БД из переменных окружения.
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "user": os.getenv("DB_USER", "annm"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
