// static/js/forgot_password.js
document.addEventListener('DOMContentLoaded', () => {
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    const verifyCodeForm = document.getElementById('verify-code-form');
    const resetPasswordForm = document.getElementById('reset-password-form');

    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('forgot-password-email').value;

        const response = await fetch('/forgot_password/send_verification_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ email })
        });

        if (response.ok) {
            forgotPasswordForm.style.display = 'none';
            verifyCodeForm.style.display = 'flex';
        } else {
            const error = await response.json();
            alert(error.message);
        }
    });

    verifyCodeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('forgot-password-email').value;
        const code = document.getElementById('verification-code').value;

        const response = await fetch('/forgot_password/verify_code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ email, code })
        });

        if (response.ok) {
            verifyCodeForm.style.display = 'none';
            resetPasswordForm.style.display = 'flex';
        } else {
            const error = await response.json();
            alert(error.message);
        }
    });

    resetPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('forgot-password-email').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmNewPassword = document.getElementById('confirm-new-password').value;

        if (newPassword !== confirmNewPassword) {
            alert('Passwords do not match');
            return;
        }

        const response = await fetch('/forgot_password/reset_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ email, new_password: newPassword })
        });

        if (response.redirected) {
            window.location.href = response.url;
        } else {
            const error = await response.json();
            alert(error.message);
        }
    });
});