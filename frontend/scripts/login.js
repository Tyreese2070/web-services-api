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

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous messages
    document.getElementById('error-message').style.display = 'none';
    document.getElementById('success-message').style.display = 'none';
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();
    
    if (!username || !password) {
        showError('Please enter both username and password');
        return;
    }
    
    try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Login successful! Redirecting...');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showError(data.Error || 'Login failed. Please try again.');
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
