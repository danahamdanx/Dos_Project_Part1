const CATALOG_URL = "http://localhost:5001";
const ORDER_URL = "http://localhost:5002";


/*const CATALOG_URL = "http://catalog-service:5001";
const ORDER_URL = "http://order-service:5002";
*/
async function searchBooks() {
    const topic = document.getElementById("topicInput").value;
    const response = await fetch(`${CATALOG_URL}/search/${topic}`);
    const books = await response.json();

    let html = "<h3>Search Results:</h3>";

    books.forEach(book => {
        html += `
            <div class="book-card">
                <div class="book-title">${book.title} (ID: ${book.id})</div>
                <div class="book-info">Topic: ${book.topic}</div>
                <div class="book-info">Price: $${book.price} — Quantity: ${book.quantity}</div>
                <div class="buttons">
                    <button onclick="info(${book.id})">Info</button>
                    <button onclick="purchase(${book.id})">Buy</button>
                </div>
            </div>
        `;
    });

    document.getElementById("results").innerHTML = html;
}

async function info(id) {
    const response = await fetch(`${CATALOG_URL}/info/${id}`);
    const book = await response.json();
    alert(`Title: ${book.title}\nTopic: ${book.topic}\nPrice: $${book.price}\nQuantity: ${book.quantity}`);
}

async function purchase(id) {
    const response = await fetch(`${ORDER_URL}/purchase/${id}`, { method: "POST" });
    const result = await response.json();

    if (result.success) {
        alert(`✅ Purchase Successful\nNew Quantity: ${result.new_quantity}`);
    } else {
        alert("❌ " + result.message);
    }

    searchBooks(); // refresh results
}
