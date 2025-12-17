import sqlite3

DB = "catalog.db"

books = [
    # ===== Lab 1 books =====
    (1, "How to get a good grade in DOS in 40 minutes a day", "distributed systems", 40, 5),
    (2, "RPCs for Noobs", "distributed systems", 50, 5),
    (3, "Xen and the Art of Surviving Undergraduate School", "undergraduate school", 30, 5),
    (4, "Cooking for the Impatient Undergrad", "undergraduate school", 25, 5),

    # ===== Lab 2 NEW books =====
    (5, "How to finish Project 3 on time", "distributed systems", 45, 5),
    (6, "Why theory classes are so hard", "theory", 35, 5),
    (7, "Spring in the Pioneer Valley", "fiction", 20, 5),
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    topic TEXT NOT NULL,
    price INTEGER NOT NULL,
    quantity INTEGER NOT NULL
)
""")

# Clear table to ensure consistent replicas
cur.execute("DELETE FROM books")

# Insert all books
cur.executemany(
    "INSERT INTO books (id, title, topic, price, quantity) VALUES (?, ?, ?, ?, ?)",
    books
)

conn.commit()
conn.close()

print("✅ catalog.db created and initialized with Lab 1 + Lab 2 books.")
