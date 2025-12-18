import os
import requests
from flask import Flask, request, jsonify
from cache import LRUCacheTTL
from lb import RoundRobin

app = Flask(__name__)

catalog_replicas = os.getenv("CATALOG_REPLICAS", "").split(",")
order_replicas = os.getenv("ORDER_REPLICAS", "").split(",")

cat_lb = RoundRobin(catalog_replicas)
ord_lb = RoundRobin(order_replicas)

CACHE_SIZE = int(os.getenv("CACHE_SIZE", "50"))
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "30"))
cache = LRUCacheTTL(capacity=CACHE_SIZE, ttl_seconds=CACHE_TTL)

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "secret123")  # لازم يطابق compose

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
    payload = request.get_json(force=True)
    replica = ord_lb.next()
    r = requests.post(f"{replica}/buy", json=payload, timeout=3)
    return (r.text, r.status_code, {"Content-Type": "application/json"})
