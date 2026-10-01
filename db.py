import os
import re
import sys
import pymysql
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_HOST = os.getenv("MARIADB_HOST", "192.168.1.22")
DB_PORT = int(os.getenv("MARIADB_PORT", "3306"))
DB_USER = os.getenv("MARIADB_USER", "antonio")
DB_PASS = os.getenv("MARIADB_PASSWORD", "")
DB_NAME = os.getenv("MARIADB_DB", "dre_gestores")


class MariaDBRow:
    """Linha de resultado com suporte a acesso por nome de coluna (case-insensitive) e por índice numérico,
    além de compatibilidade total com dict(row) e unpacking."""
    __slots__ = ('_data', '_keys', '_values')

    def __init__(self, keys, values):
        self._keys = [k.lower() if isinstance(k, str) else k for k in keys]
        self._values = list(values)
        self._data = {}
        for k, orig_k, v in zip(self._keys, keys, values):
            self._data[k] = v
            if orig_k != k:
                self._data[orig_k] = v

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._values[item]
        if isinstance(item, str):
            res = self._data.get(item)
            if res is None and item.lower() in self._data:
                return self._data[item.lower()]
            return res
        raise KeyError(item)

    def get(self, item, default=None):
        try:
            val = self.__getitem__(item)
            return default if val is None else val
        except (KeyError, IndexError):
            return default

    def keys(self):
        return self._keys

    def values(self):
        return self._values

    def items(self):
        return [(k, self._data[k]) for k in self._keys]

    def __iter__(self):
        return iter(self._keys)

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        return f"MariaDBRow({dict(self.items())})"


def convert_placeholders(sql):
    """Substitui ? por %s fora de strings literais para garantir compatibilidade com PyMySQL."""
    parts = re.split(r"('(?:''|[^'])*'|\"(?:\"\"|[^\"])*\")", sql)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace("?", "%s")
    return "".join(parts)


class MariaDBCursor:
    def __init__(self, raw_cursor):
        self._cur = raw_cursor
        self.description = None

    def execute(self, sql, params=None):
        sql_converted = convert_placeholders(sql)
        if params is not None:
            if isinstance(params, list):
                params = tuple(params)
            self._cur.execute(sql_converted, params)
        else:
            self._cur.execute(sql_converted)
        self.description = self._cur.description
        return self

    def executemany(self, sql, seq_of_params):
        sql_converted = convert_placeholders(sql)
        return self._cur.executemany(sql_converted, seq_of_params)

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None or not self.description:
            return None
        keys = [d[0] for d in self.description]
        return MariaDBRow(keys, row)

    def fetchall(self):
        rows = self._cur.fetchall()
        if not rows or not self.description:
            return []
        keys = [d[0] for d in self.description]
        return [MariaDBRow(keys, r) for r in rows]

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def lastrowid(self):
        return self._cur.lastrowid

    def close(self):
        self._cur.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MariaDBConnection:
    def __init__(self, **kwargs):
        config = {
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_USER,
            'password': DB_PASS,
            'database': DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': False
        }
        config.update(kwargs)
        self._kwargs = config
        self._conn = pymysql.connect(**config)

    def cursor(self):
        return MariaDBCursor(self._conn.cursor())

    def execute(self, sql, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()


def get_db_connection():
    return MariaDBConnection()


def get_db():
    return MariaDBConnection()
