import os
import requests
from flask import Flask, request, jsonify
from cache import LRUCacheTTL
from lb import RoundRobin
import json

app = Flask(__name__)

catalog_replicas = os.getenv("CATALOG_REPLICAS", "").split(",")
order_replicas = os.getenv("ORDER_REPLICAS", "").split(",")

cat_lb = RoundRobin(catalog_replicas)
ord_lb = RoundRobin(order_replicas)

CACHE_SIZE = int(os.getenv("CACHE_SIZE", "50"))
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "30"))
cache = LRUCacheTTL(capacity=CACHE_SIZE, ttl_seconds=CACHE_TTL)

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "secret123")  # compose

# ---- internal endpoint to accept invalidations from replicas ----
@app.post("/internal/cache/invalidate")
def internal_cache_invalidate():
    data = request.get_json(force=True)
    if data.get("token") != INTERNAL_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    book_id = int(data["book_id"])
    cache.invalidate(f"book:{book_id}")
    return jsonify({"ok": True, "invalidated": book_id})

# ---- READ (Query) with cache ----
@app.get("/query/<int:book_id>")
def query_book(book_id):
    key = f"book:{book_id}"
    hit = cache.get(key)
    if hit is not None:
        return jsonify({"source": "cache", "data": hit})

    replica = cat_lb.next()
    r = requests.get(f"{replica}/info/{book_id}", timeout=3)
    r.raise_for_status()
    data = r.json()
    cache.put(key, data)
    return jsonify({"source": replica, "data": data})

# ---- WRITE (Buy/Order) no cache ----
@app.post("/buy")
def buy_book():
    payload = None

    # 1️⃣ حاول JSON طبيعي
    if request.is_json:
        payload = request.get_json(silent=True)

    # 2️⃣ إذا فشل، جرّبي raw
    if not payload and request.data:
        try:
            import json
            payload = json.loads(request.data.decode("utf-8"))
        except Exception:
            pass

    # 3️⃣ إذا فشل، جرّبي form
    if not payload and request.form:
        payload = request.form.to_dict()

    if not payload:
        return jsonify({"error": "invalid or missing request body"}), 400

    book_id = payload.get("book_id")
    if not book_id:
        return jsonify({"error": "missing book_id"}), 400

    replica = ord_lb.next()
    r = requests.post(
        f"{replica}/check_and_decrement/{book_id}",
        timeout=3
    )

    return (r.text, r.status_code, {"Content-Type": "application/json"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
