// Add input event listeners to validate fields on input
document.getElementById('first_name').addEventListener('input', function() {
    validateField(this, 'First name is required.');
});

document.getElementById('last_name').addEventListener('input', function() {
    validateField(this, 'Last name is required.');
});

document.getElementById('username').addEventListener('input', function() {
    validateField(this, 'Username is required.');
});

document.getElementById('email').addEventListener('input', function() {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const errorDiv = document.getElementById('error_email');
    if (!this.value.trim()) {
        showError(errorDiv, 'Email is required.');
    } else if (!emailRegex.test(this.value)) {
        showError(errorDiv, 'Enter a valid email address.');
    } else {
        errorDiv.textContent = '';
    }
});

document.getElementById('phone_number').addEventListener('input', function() {
    validateField(this, 'Phone number is required.');
});

document.getElementById('password').addEventListener('input', function() {
    const passwordError = validatePasswordComplexity(this.value);
    const errorDiv = document.getElementById('error_password');
    if (!this.value.trim()) {
        showError(errorDiv, 'Password is required.');
    } else if (passwordError) {
        showError(errorDiv, passwordError);
    } else {
        errorDiv.textContent = '';
    }
});

document.getElementById('confirm_password').addEventListener('input', function() {
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('error_confirm_password');
    if (!this.value.trim()) {
        showError(errorDiv, 'Confirm password is required.');
    } else if (this.value !== password) {
        showError(errorDiv, 'Passwords do not match.');
    } else {
        errorDiv.textContent = '';
    }
});

function validateField(input, errorMessage) {
    const errorDiv = document.getElementById('error_' + input.id);
    if (!input.value.trim()) {
        showError(errorDiv, errorMessage);
    } else {
        errorDiv.textContent = '';
    }
}

function showError(element, message) {
    element.textContent = message;
    clearTimeout(element.timeout); // Clear any existing timeout to prevent flicker
    element.timeout = setTimeout(() => {
        element.textContent = '';
    }, 3000); // 3 seconds delay to clear the error
}

function validatePasswordComplexity(password) {
    if (password.length < 8) {
        return "Password must be at least 8 characters long.";
    }
    if (!/[A-Z]/.test(password)) {
        return "Password must contain at least one uppercase letter.";
    }
    if (!/[a-z]/.test(password)) {
        return "Password must contain at least one lowercase letter.";
    }
    if (!/[0-9]/.test(password)) {
        return "Password must contain at least one digit.";
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]/.test(password)) {
        return "Password must contain at least one special character.";
    }
    return null;
}
