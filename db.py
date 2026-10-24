import os
from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor


def connect(database=True):
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'), port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'king_cleaner'), password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'control_produccion_db') if database else None,
        charset='utf8mb4', cursorclass=DictCursor, connect_timeout=5,
        read_timeout=15, write_timeout=15, autocommit=False,
        init_command="SET time_zone = '-04:00'")


@contextmanager
def transaction():
    connection = connect()
    try:
        with connection.cursor() as cursor:
            yield cursor
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def rows(sql, params=()):
    with transaction() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchall()


def one(sql, params=()):
    found = rows(sql, params)
    return found[0] if found else None
