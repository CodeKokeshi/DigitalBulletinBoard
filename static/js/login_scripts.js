document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    // Handle Login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Prevent default form submission
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (response.redirected) {
                window.location.href = response.url; // Redirect to new page
            } else {
                const error = await response.json();
                console.error("Login failed:", error.message);
                alert(error.message);
            }

        } catch (err) {
            console.error("Error during login:", err);
            alert("An error occurred.");
        }
    });

    // Initialize to show Login form as default
    loginForm.style.display = 'flex'; // Default to Login form
});