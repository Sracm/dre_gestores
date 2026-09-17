import sqlite3
db = sqlite3.connect('dre_cache.db')
print(db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
