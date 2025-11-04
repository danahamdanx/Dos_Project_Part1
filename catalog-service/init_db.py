import sqlite3

DB = 'catalog.db'

books = [
    (1, "How to get a good grade in DOS in 40 minutes a day", "distributed systems", 40, 5),
    (2, "RPCs for Noobs", "distributed systems", 50, 5),
    (3, "Xen and the Art of Surviving Undergraduate School", "undergraduate school", 30, 5),
    (4, "Cooking for the Impatient Undergrad", "undergraduate school", 25, 5)
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

# create table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    price INTEGER NOT NULL,
    quantity INTEGER NOT NULL
)
''')

# clear table
cur.execute("DELETE FROM books")

# insert books
cur.executemany(
    "INSERT INTO books (id, title, topic, price, quantity) VALUES (?, ?, ?, ?, ?)",
    books
)

conn.commit()
conn.close()

print("✅ catalog.db created and initialized successfully.")
