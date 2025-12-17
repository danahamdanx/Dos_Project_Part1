from flask import Flask, jsonify, request, abort
import sqlite3
from flask_cors import CORS

DB = 'catalog.db'
app = Flask(__name__)
CORS(app)

def row_to_dict(r):
    return {"id": r[0], "title": r[1], "topic": r[2], "price": r[3], "quantity": r[4]}

@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id,title,topic,price,quantity FROM books WHERE topic LIKE ?", (f"%{topic}%",))
    rows = cur.fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])

@app.route('/info/<int:item_id>', methods=['GET'])
def info(item_id):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id,title,topic,price,quantity FROM books WHERE id = ?", (item_id,))
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
    return jsonify({"success": True, "new_quantity": new_qty})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)