document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/login/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
    });

    const data = await response.json();

    if (data.success) {
        console.log("Access Token:", data.access_token);
        localStorage.setItem("access_token", data.access_token);  // Store token
        window.location.href = "";  // Redirect user
    } else {
        alert(data.error || "Login failed");
    }
});
