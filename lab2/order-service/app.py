import os
import sqlite3
import requests
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

# Environment configuration
PORT = int(os.getenv("PORT", "5001"))
REPLICA_ID = os.getenv("REPLICA_ID", "replica1")
PEER_URL = os.getenv("PEER_URL")  # URL of peer replica
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "secret123")
DB = os.getenv("DB_PATH", "catalog.db")

app = Flask(__name__)
CORS(app)

# --- Helper functions ---
def row_to_dict(r):
    return {"id": r[0], "title": r[1], "topic": r[2], "price": r[3], "quantity": r[4]}

def replicate_to_peer(payload: dict, path: str):
    """Send a write operation to the peer replica, if configured."""
    if not PEER_URL:
        return
    try:
        requests.post(f"{PEER_URL}{path}", json={"token": INTERNAL_TOKEN, **payload}, timeout=2)
    except Exception:
        pass

# --- Catalog endpoints ---
@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, title, topic, price, quantity FROM books WHERE topic LIKE ?", (f"%{topic}%",))
    rows = cur.fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/info/<int:item_id>', methods=['GET'])
def info(item_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, title, topic, price, quantity FROM books WHERE id = ?", (item_id,))
    r = cur.fetchone()
    conn.close()
    if not r:
        abort(404, "Item not found")
    return jsonify(row_to_dict(r))

@app.route('/check_and_decrement/<int:item_id>', methods=['POST'])
def check_and_decrement(item_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT quantity FROM books WHERE id = ?", (item_id,))
    r = cur.fetchone()
    if not r:
        conn.close()
        return jsonify({"success": False, "error": "not_found"}), 404

    qty = r[0]
    if qty <= 0:
        conn.close()
        return jsonify({"success": False, "error": "out_of_stock"}), 409

    cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (item_id,))
    conn.commit()
    cur.execute("SELECT quantity FROM books WHERE id = ?", (item_id,))
    new_qty = cur.fetchone()[0]
    conn.close()

    # Replicate decrement to peer
    replicate_to_peer({"item_id": item_id}, "/internal/replicate/decrement")
    return jsonify({"success": True, "new_quantity": new_qty})

# --- Internal replication endpoints ---
@app.post("/internal/replicate/decrement")
def internal_replicate_decrement():
    data = request.get_json(force=True)
    if data.get("token") != INTERNAL_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"error": "missing item_id"}), 400

    # Apply decrement locally
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ? AND quantity > 0", (item_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "replica": REPLICA_ID})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
