document.addEventListener('DOMContentLoaded', () => {
    const forgotPasswordForm = document.getElementById('forgot-password-form');
    const verifyCodeForm = document.getElementById('verify-code-form');
    const resetPasswordForm = document.getElementById('reset-password-form');
    const forgotPasswordError = document.getElementById('forgot-password-error');
    const verifyCodeError = document.getElementById('verify-code-error');

    const disableForm = (form) => {
        const inputs = form.querySelectorAll('input, button');
        inputs.forEach(input => input.disabled = true);
    };

    const enableForm = (form) => {
        const inputs = form.querySelectorAll('input, button');
        inputs.forEach(input => input.disabled = false);
    };

    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        disableForm(forgotPasswordForm);
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
            forgotPasswordError.style.display = 'block';
            forgotPasswordError.textContent = error.message || 'Email not found.';
            enableForm(forgotPasswordForm);
        }
    });

    verifyCodeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        disableForm(verifyCodeForm);
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
            verifyCodeError.style.display = 'block';
            verifyCodeError.textContent = error.message || 'Invalid verification code.';
            enableForm(verifyCodeForm);
        }
    });

    resetPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        disableForm(resetPasswordForm);
        const email = document.getElementById('forgot-password-email').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmNewPassword = document.getElementById('confirm-new-password').value;

        if (newPassword !== confirmNewPassword) {
            const resetPasswordError = document.getElementById('reset-password-error');
            resetPasswordError.style.display = 'block';
            resetPasswordError.textContent = 'Passwords do not match.';
            enableForm(resetPasswordForm);
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
            const resetPasswordError = document.getElementById('reset-password-error');
            resetPasswordError.style.display = 'block';
            resetPasswordError.textContent = error.message || 'Failed to reset password.';
            enableForm(resetPasswordForm);
        }
    });
});
