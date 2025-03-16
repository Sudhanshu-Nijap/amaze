document.getElementById("add-price-watch").addEventListener("click", function () {
    const desiredPrice = parseFloat(document.getElementById("desired-price").value) || 0;
    const currentPrice = parseFloat(document.getElementById("product-price").textContent.replace(/[^\d.]/g, '')) || 0;

    if (desiredPrice <= 0) {
        alert("Please enter a valid desired price.");
        return;
    }

    const productData = {
        asin: this.dataset.asin,
        title: this.dataset.title,
        image_url: this.dataset.imageurl,
        amazon_url: this.dataset.url,
        rating: this.dataset.rating,
        stock_status: this.dataset.stockStatus,
        desired_price: desiredPrice,
        current_price: currentPrice
    };

    fetch("/track-products-db/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: JSON.stringify(productData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Product successfully added to your watchlist!');
        } else {
            alert(`❌ ${data.error || 'Failed to add product.'}`);
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
        alert('Something went wrong. Please try again.');
    });
});

// CSRF Token Retrieval for AJAX Requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.split('=')[1]);
                break;
            }
        }
    }
    return cookieValue;
}
