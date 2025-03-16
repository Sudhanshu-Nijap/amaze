document.addEventListener("DOMContentLoaded", function () { 
    console.log("scroll.js is loaded");  // Debugging check

    let start = 8; // Initial start index for pagination
    const container = document.getElementById("product-container");
    let isLoading = false; // Prevent multiple requests

    if (!container) {
        console.error("Error: #product-container not found");
        return;  // Stop execution if container is missing
    }

    // Event listener for scroll to load more products
    container.addEventListener("scroll", function () {
        if (isLoading) return;

        // Check if the user has scrolled to the end
        if (container.scrollLeft + container.clientWidth >= container.scrollWidth - 10) {
            console.log("Fetching more products...");
            loadMoreProducts();
        }
    });

    // Function to load more products from backend
    function loadMoreProducts() {
        isLoading = true;
        fetch(`/load-more-products?start=${start}`)
            .then(response => response.json())
            .then(data => {
                if (data.products.length > 0) {
                    data.products.forEach(product => {
                        let productCard = document.createElement("div");
                        productCard.classList.add("product-card");
                        productCard.innerHTML = `
                        <div class="card flex-shrink-0 border-secondary mx-2" style="width: 18rem; height: 24.5rem;">
                            <a href="{% url 'result' %}?url=${encodeURIComponent(product.url)}">
                                <img src="${product.image}" class="card-img-top p-2 mt-3" alt="${product.title}"
                                    style="height: auto; max-height: 10rem; object-fit: contain; width: 100%;">
                            </a>
                            <div class="card-body d-flex flex-column">
                                <a href="{% url 'result' %}?url=${encodeURIComponent(product.url)}" style="text-decoration: none !important; color: black !important;">
                                    <p class="card-title title-clamp px-2"">${ product.title }</p>
                                </a>
                                <p class="fw-bold text-center my-2 mt-auto">${ product.price }</p>
                                
                                <a href="${ product.url }" target="_blank" class="btn btn-warning mt-auto">View at Amazon</a>
                            </div>
                        </div>
                        `;
                        container.appendChild(productCard);
                    });
                    start += 8; // Increment the start index
                    isLoading = false;
                } else {
                    console.log("No more products to load.");
                }
            })
            .catch(error => {
                console.error("Error fetching products:", error);
                isLoading = false;
            });
    }

    // Initial load of products when page is loaded
    loadMoreProducts();
});


// for today deals
document.addEventListener("DOMContentLoaded", function () { 
    console.log("scroll.js is loaded");  // Debugging check

    let start = 8; // Initial start index for pagination
    const container = document.getElementById("product_deals-container");
    let isLoading = false; // Prevent multiple requests

    if (!container) {
        console.error("Error: #product_deals-container not found");
        return;  // Stop execution if container is missing
    }

    // Event listener for scroll to load more products
    container.addEventListener("scroll", function () {
        if (isLoading) return;

        // Check if the user has scrolled to the end
        if (container.scrollLeft + container.clientWidth >= container.scrollWidth - 10) {
            console.log("Fetching more products...");
            load_deal_products();
        }
    });

    // Function to load more products from backend
    function loadTodayProducts() {
        isLoading = true;
        fetch(`/load-deal-products?start=${start}`)
            .then(response => response.json())
            .then(data => {
                if (data.products.length > 0) {
                    data.products.forEach(product => {
                        let productCard = document.createElement("div");
                        productCard.classList.add("product-card");
                        productCard.innerHTML = `
                        <div class="card flex-shrink-0 border-secondary mx-2" style="width: 18rem; height: 24.5rem;">
                            <a href="{% url 'result' %}?url=${encodeURIComponent(product.url)}">
                                <img src="${product.image}" class="card-img-top p-2 mt-3" alt="${product.title}"
                                    style="height: auto; max-height: 10rem; object-fit: contain; width: 100%;">
                            </a>
                            <div class="card-body d-flex flex-column">
                                <a href="{% url 'result' %}?url=${encodeURIComponent(product.url)}" style="text-decoration: none !important; color: black !important;">
                                    <p class="card-title title-clamp px-2"">${ product.title }</p>
                                </a>
                                <p class="fw-bold text-center my-2 mt-auto">${ product.price }</p>
                                
                                <a href="${ product.url }" target="_blank" class="btn btn-warning mt-auto">View at Amazon</a>
                            </div>
                        </div>
                        `;
                        container.appendChild(productCard);
                    });
                    start += 8; // Increment the start index
                    isLoading = false;
                } else {
                    console.log("No more products to load.");
                }
            })
            .catch(error => {
                console.error("Error fetching products:", error);
                isLoading = false;
            });
    }

    // Initial load of products when page is loaded
    loadTodayProducts();
});
