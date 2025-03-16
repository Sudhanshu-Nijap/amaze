document.addEventListener("DOMContentLoaded", function () { 
    // Get the product price from the <h3> tag (removing ₹ and commas)
    const productPrice = parseFloat(document.getElementById("product-price").textContent.replace(/[^0-9.]/g, "")) || 0;

    // Get input field for the desired price
    const desiredPriceInput = document.getElementById("desired-price");

    // Get all the discount buttons
    const discountButtons = document.querySelectorAll(".btn-outline-secondary");

    discountButtons.forEach(button => {
        button.addEventListener("click", function () {
            const discountText = this.textContent.trim(); // e.g., "-3%" or "Any Price Drop!"

            if (discountText.includes("%")) {
                // Extract percentage (e.g., "-3%" -> 3)
                const discount = parseFloat(discountText.replace("%", "").replace("-", ""));
                const newPrice = productPrice - (productPrice * discount / 100);
                desiredPriceInput.value = newPrice.toFixed(2); // Update the input with 2 decimal places
            } else {
                // If "Any Price Drop!" is clicked, reduce the price by ₹1
                desiredPriceInput.value = (productPrice - 1).toFixed(2);
            }
        });
    });
});
