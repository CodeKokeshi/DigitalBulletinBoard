document.addEventListener('DOMContentLoaded', () => {
    const loginToggle = document.getElementById('login-toggle');
    const signupToggle = document.getElementById('signup-toggle');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const signupButton = document.getElementById('signup-button');
    const termsCheckbox = document.getElementById('terms-checkbox');

    // Function to update the active button based on the visible form
    function updateActiveButton() {
        if (signupForm.style.display === 'flex') {
            loginToggle.classList.remove('active');
            signupToggle.classList.add('active');
        } else {
            signupToggle.classList.remove('active');
            loginToggle.classList.add('active');
        }
    }

    // Event listener for Login button
    loginToggle.addEventListener('click', () => {
        loginForm.style.display = 'flex'; // Show login form
        signupForm.style.display = 'none'; // Hide signup form
        updateActiveButton(); // Update button styles
    });

    // Event listener for Signup button
    signupToggle.addEventListener('click', () => {
        loginForm.style.display = 'none'; // Hide login form
        signupForm.style.display = 'flex'; // Show signup form
        updateActiveButton(); // Update button styles
    });

    // Event listener to enable/disable Signup button based on checkbox
    termsCheckbox.addEventListener('change', () => {
        signupButton.disabled = !termsCheckbox.checked; // Enable if terms are checked
    });

    // Handle Signup form submission
// Handle Signup form submission
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fullName = document.getElementById('full-name').value;
        const age = document.getElementById('age').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;

        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ fullName, age, email, password }),
            });

            if (response.redirected) {
                window.location.href = response.url; // Redirect to verification page
            } else {
                const error = await response.json();
                alert(error.message || 'Signup failed');
            }
        } catch (err) {
            console.error('Error during signup:', err);
            alert('An error occurred.');
        }
    });




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
    signupForm.style.display = 'none'; // Hide Signup form
    updateActiveButton(); // Set active button correctly
});
