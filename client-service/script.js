/*const CATALOG_URL = "http://localhost:5001";
const ORDER_URL = "http://localhost:5002";
*/

const CATALOG_URL = "http://catalog-service:5001";
const ORDER_URL = "http://order-service:5002";

//  Search function
async function searchBooks() {
    const topic = document.getElementById("topicInput").value;

    const response = await fetch(`${CATALOG_URL}/search/${topic}`);
    const books = await response.json();

    let html = "<h3>Search Results:</h3>";

    books.forEach(book => {
        html += `
            <p>
                <b>${book.title}</b> (ID: ${book.id}) — $${book.price} — qty: ${book.quantity}
                <button onclick="info(${book.id})">Info</button>
                <button onclick="purchase(${book.id})">Buy</button>
            </p>
        `;
    });

    document.getElementById("results").innerHTML = html;
}

//  View more details about the book
async function info(id) {
    const response = await fetch(`${CATALOG_URL}/info/${id}`);
    const book = await response.json();

    alert(`
Title: ${book.title}
Topic: ${book.topic}
Price: $${book.price}
Quantity available: ${book.quantity}
    `);
}

//  Purchase function
async function purchase(id) {
    const response = await fetch(`${ORDER_URL}/purchase/${id}`, { method: "POST" });
    const result = await response.json();

    if (result.success) {
        alert(` Purchase Successful\nNew Quantity: ${result.new_quantity}`);
    } else {
        alert("error " + result.message);
    }

    searchBooks(); // refresh search results after purchase
}
