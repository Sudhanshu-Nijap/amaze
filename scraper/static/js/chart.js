document.addEventListener("DOMContentLoaded", function () {
    const priceHistoryElement = document.getElementById("price-history-data");
    let priceHistoryData = [];

    if (priceHistoryElement) {
        try {
            priceHistoryData = JSON.parse(priceHistoryElement.textContent);
        } catch (error) {
            console.error("Error parsing price history data:", error);
            return;
        }
    }

    // Ensure price history data is an array
    if (!Array.isArray(priceHistoryData) || priceHistoryData.length === 0) {
        console.warn("No price history data available.");
        return;
    }

    // Extract labels (dates) and prices, ensuring valid numbers
    const labels = [];
    const prices = [];

    priceHistoryData.forEach(item => {
        const date = item.date;
        const price = parseFloat(item.price);

        if (!isNaN(price)) {
            labels.push(date);
            prices.push(price);
        }
    });

    if (prices.length === 0) {
        console.warn("No valid price data available.");
        return;
    }

    const ctx = document.getElementById("priceHistoryChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Price (₹)",
                data: prices,
                borderColor: "#007bff",
                backgroundColor: "rgba(0, 123, 255, 0.1)",
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: "Date" }
                },
                y: {
                    title: { display: true, text: "Price (₹)" },
                    suggestedMin: Math.min(...prices) * 0.95, // 5% lower than min price
                    suggestedMax: Math.max(...prices) * 1.05  // 5% higher than max price
                }
            }
        }
    });
});
