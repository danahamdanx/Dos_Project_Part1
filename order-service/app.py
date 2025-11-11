from flask import Flask, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

CATALOG_URL = "http://catalog-service:5001"
orders_log = "orders.txt"

@app.route("/purchase/<int:item_id>", methods=["POST"])
def purchase(item_id):
    r = requests.post(f"{CATALOG_URL}/check_and_decrement/{item_id}")
    if r.status_code == 200:
        data = r.json()
        with open(orders_log, "a") as file:
            file.write(f"bought book id={item_id}\n")
        return jsonify({
            "success": True,
            "message": f"Book {item_id} purchased successfully",
            "new_quantity": data["new_quantity"]
        })
    elif r.status_code == 409:
        return jsonify({"success": False, "message": "Out of stock"}), 409
    else:
        return jsonify({"success": False, "message": "Book not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)
