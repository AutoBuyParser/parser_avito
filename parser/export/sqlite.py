import sqlite3

from pathlib import Path

from models import Item
from states_enum import ProductState
from parser.export.base import ResultStorage


class SQLiteStorage(ResultStorage):
    name = "sqlite"

    def __init__(self, db_name: Path):
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS states (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE
                )
                """
            )

            cursor.execute(f"SELECT COUNT(*) FROM states")
            count = cursor.fetchone()[0]
            if count == 0:
                states = [
                    (1, "new"),
                    (2, "basket"),
                    (3, "buy"),
                    (4, "unavailable"),
                    (5, "error"),
                    (6, "old"),
                    (7, "reserved"),
                    (8, "unidentified"),
                    (9, "expensive"),
                ]
                cursor.executemany(
                    f"INSERT INTO states (id, name) VALUES (?, ?)", states
                )

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER,
                    price INTEGER,
                    title TEXT,
                    url TEXT,
                    state INTEGER,
                    notes TEXT,
                    FOREIGN KEY(state) REFERENCES states(id)
                )
                """
            )

            conn.commit()

    def save(self, ads: list[Item]):
        for ad in ads:
            if self.record_exists(ad.id):
                continue
            self.add_record(
                ad.id,
                ad.priceDetailed.value,
                ad.title,
                "https://www.avito.ru" + ad.urlPath,
                ProductState.NEW.value
            )

    def add_record(self, record_id, price, title, url, state, notes: str | None = None):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO products (id, price, title, url, state, notes) VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, price, title, url, state, notes),
            )
            conn.commit()

    def record_exists(self, record_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM products WHERE id = ?",
                (record_id,),
            )
            return cursor.fetchone() is not None

    def get_product_by_id(self, record_id: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, price, title, url, state, notes FROM products WHERE id = ?",
                (record_id,),
            )
            row = cursor.fetchone()
            return row if row else None

    def get_product_by_title_and_price(self, title: str, price: int):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, price, title, url, state, notes FROM products WHERE title = ? AND price = ?",
                (title, price,),
            )
            row = cursor.fetchone()
            return row if row else None

    def update_state(self, record_id, new_state_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE products SET state = ? WHERE id = ?",
                (new_state_id, record_id),
            )
            conn.commit()

    def update_notes(self, record_id, new_notes):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE products SET notes = ? WHERE id = ?",
                (new_notes, record_id),
            )
            conn.commit()

    def get_state_name(self, state_id):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT name FROM products WHERE id = ?",
                (state_id,),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def get_new_products(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT id, price, title, url, state, notes FROM products WHERE state = ?",
                (ProductState.NEW.value,),
            )
            return cursor.fetchall()
