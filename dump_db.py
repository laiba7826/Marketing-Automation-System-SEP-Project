import sqlite3
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"--- {table['name']} ---")
    rows = conn.execute(f"SELECT * FROM {table['name']} LIMIT 5").fetchall()
    for row in rows:
        print(dict(row))
conn.close()
