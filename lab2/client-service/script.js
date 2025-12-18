
/*const CATALOG_URL = "http://localhost:5001";
const ORDER_URL = "http://localhost:5002";*/
const CLIENT_URL = "http://localhost:5000";

async function searchBooks() {
    const topic = document.getElementById("topicInput").value;
    try {
        const response = await fetch(`${CLIENT_URL}/search/${topic}`);
        if (!response.ok) throw new Error("Catalog service error");
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
    } catch (err) {
        alert("Error fetching books: " + err.message);
    }
}

async function info(id) {
    try {
        const response = await fetch(`${CLIENT_URL}/query/${id}`);
        if (!response.ok) throw new Error("Catalog service error");
        const book = await response.json();
        alert(`Title: ${book.title}\nTopic: ${book.topic}\nPrice: $${book.price}\nQuantity: ${book.quantity}`);
    } catch (err) {
        alert("Error fetching book info: " + err.message);
    }
}

async function purchase(id) {
    try {
const response = await fetch(`${CLIENT_URL}/buy`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ book_id: id })
});
        if (!response.ok) throw new Error("Order service error");
        const result = await response.json();

        if (result.success) {
            alert(`✅ Purchase Successful\nNew Quantity: ${result.new_quantity}`);
        } else {
            alert("❌ " + result.message);
        }

        searchBooks(); // refresh results
    } catch (err) {
        alert("Error processing purchase: " + err.message);
    }
}
