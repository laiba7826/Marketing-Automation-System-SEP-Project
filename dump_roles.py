import sqlite3
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
roles = conn.execute('SELECT * FROM site_roles').fetchall()
for r in roles:
    print(dict(r))
conn.close()
