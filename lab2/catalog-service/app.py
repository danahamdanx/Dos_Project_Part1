import os
import sqlite3
import requests
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# =====================
# Configuration
# =====================
DB = "catalog.db"

PORT = int(os.getenv("PORT", "5001"))
REPLICA_ID = os.getenv("REPLICA_ID", "catalogX")
PEER_URL = os.getenv("PEER_URL")  
# example: http://catalog-2:5001

INVALIDATE_URL = os.getenv(
    "FRONTEND_CACHE_INVALIDATE_URL"
)  
# example: http://frontend:5000/invalidate

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "secret123")

# =====================
# Helpers
# =====================
def row_to_dict(r):
    return {
        "id": r[0],
        "title": r[1],
        "topic": r[2],
        "price": r[3],
        "quantity": r[4],
    }

def get_db():
    return sqlite3.connect(DB, check_same_thread=False)

# =====================
# Cache Invalidation
# =====================
def invalidate_cache(book_id: int):
    if not INVALIDATE_URL:
        return
    try:
        requests.post(
            INVALIDATE_URL,
            json={"book_id": book_id, "token": INTERNAL_TOKEN},
            timeout=2
        )
    except Exception:
        pass

# =====================
# Replication
# =====================
def replicate_to_peer(book_id: int, new_stock: int):
    if not PEER_URL:
        return
    try:
        requests.post(
            f"{PEER_URL}/internal/replicate/update_stock",
            json={
                "token": INTERNAL_TOKEN,
                "book_id": book_id,
                "new_stock": new_stock
            },
            timeout=2
        )
    except Exception:
        pass

# =====================
# Public Catalog APIs
# =====================
@app.get("/search/<topic>")
def search(topic):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM books WHERE topic LIKE ?",
        (f"%{topic}%",)
    )
    rows = cur.fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.get("/info/<int:book_id>")
def info(book_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE id=?", (book_id,))
    r = cur.fetchone()
    conn.close()

    if not r:
        abort(404, "Book not found")

    return jsonify(row_to_dict(r))

# =====================
# Write Path (Buy)
# =====================
@app.post("/check_and_decrement/<int:book_id>")
def check_and_decrement(book_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
    r = cur.fetchone()

    if not r:
        conn.close()
        return jsonify({"success": False, "error": "not_found"}), 404

    if r[0] <= 0:
        conn.close()
        return jsonify({"success": False, "error": "out_of_stock"}), 409

    # 🔥 Invalidate cache BEFORE write
    invalidate_cache(book_id)

    # Update local DB
    cur.execute(
        "UPDATE books SET quantity = quantity - 1 WHERE id=?",
        (book_id,)
    )
    conn.commit()

    cur.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
    new_qty = cur.fetchone()[0]
    conn.close()

    # 🔁 Replicate write to peer
    replicate_to_peer(book_id, new_qty)

    return jsonify({
        "success": True,
        "new_quantity": new_qty,
        "replica": REPLICA_ID
    })

# =====================
# Internal Replication Endpoint
# =====================
@app.post("/internal/replicate/update_stock")
def internal_replicate_update_stock():
    data = request.get_json(force=True)

    if data.get("token") != INTERNAL_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    book_id = int(data["book_id"])
    new_stock = int(data["new_stock"])

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE books SET quantity=? WHERE id=?",
        (new_stock, book_id)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "ok": True,
        "replica": REPLICA_ID,
        "book_id": book_id,
        "quantity": new_stock
    })

# =====================
# Startup
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
