document.querySelectorAll(".remove-price-watch").forEach(button => {
    button.addEventListener("click", function () {
        const asin = this.dataset.asin;

        if (!confirm(`Are you sure you want to remove "${this.dataset.title}" from your Price Watch?`)) {
            return;
        }

        fetch(`/remove-product-db/${asin}/`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")  // CSRF token for security
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('✅ Product removed successfully!');
                window.location.reload();  // Reload the page after successful deletion
            } else {
                alert(`❌ ${data.error || 'Failed to remove product.'}`);
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            alert('Something went wrong. Please try again.');
        });
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
