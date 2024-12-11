document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    const signupButton = document.getElementById('signup-button');
    const termsCheckbox = document.getElementById('terms-checkbox');
    const goBackButton = document.getElementById('go-back-button');

    // Event listener to enable/disable Signup button based on checkbox
    termsCheckbox.addEventListener('change', () => {
        signupButton.disabled = !termsCheckbox.checked; // Enable if terms are checked
    });

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

    // Initialize to show Signup form as default
    signupForm.style.display = 'flex'; // Default to Signup form
});