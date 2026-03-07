function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous messages
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('success-message').style.display = 'none';
    
    const firstName = document.getElementById('first-name').value.trim();
    const lastName = document.getElementById('last-name').value.trim();
    const email = document.getElementById('email').value.trim();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    const passwordConfirm = document.getElementById('password-confirm').value.trim();
    
    if (!firstName || !lastName || !email || !username || !password || !passwordConfirm) {
        showError('Please fill in all fields');
        return;
    }
    
    if (password !== passwordConfirm) {
        showError('Passwords do not match');
        return;
    }
    
    if (password.length < 6) {
        showError('Password must be at least 6 characters long');
        return;
    }
    
    try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch('/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                first_name: firstName,
                last_name: lastName,
                email: email,
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Registration successful! Redirecting to login...');
            setTimeout(() => {
                window.location.href = '/login/';
            }, 1500);
        } else {
            showError(data.Error || 'Registration failed. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('An error occurred. Please try again.');
    }
});

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    } else {
        alert(message);
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
    }
}
