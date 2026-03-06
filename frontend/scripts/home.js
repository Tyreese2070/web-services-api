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
const csrftoken = getCookie('csrftoken');

// LOGOUT
function logout() {
    fetch('/api/logout/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken }
    }).then(() => { window.location.href = '/login/'; });
}

// PANTRY
function loadPantry() {
    fetch('/api/pantry/')
        .then(res => res.json())
        .then(data => {
            const list = document.getElementById('pantry-list');
            list.innerHTML = '';
            if(data.length === 0) {
                list.innerHTML = '<p>Your pantry is empty.</p>';
                return;
            }
            data.forEach(item => {
                const div = document.createElement('div');
                div.className = 'pantry-item';
                const qty = item.quantity ? item.quantity : 'Not specified';
                
                div.innerHTML = `
                    <div><strong>${item.name}</strong> (Quantity: ${qty})</div>
                    <div>
                        <button onclick="updatePantry('${item.name}')">Update Quantity</button>
                        <button onclick="removeFromPantry('${item.name}')">Delete</button>
                    </div>
                `;
                list.appendChild(div);
            });
        });
}

// CREATE
function addToPantry() {
    const name = document.getElementById('new-item-name').value;
    if(!name) return;
    
    fetch('/api/pantry/add/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ name: name })
    })
    .then(res => res.json().then(data => ({ status: res.status, body: data })))
    .then(({ status, body }) => {
        if (status !== 200 && status !== 201) {
            alert(body.error || 'Unable to add ingredient');
            return;
        }
        document.getElementById('new-item-name').value = '';
        loadPantry(); // Refresh list
    });
}

// UPDATE
function updatePantry(name) {
    const newQty = prompt(`Enter new quantity for ${name}:`);
    if(newQty === null) return;

    fetch('/api/pantry/update/', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ name: name, quantity: newQty })
    }).then(() => loadPantry());
}

// DELETE
function removeFromPantry(name) {
    if(!confirm(`Remove ${name} from pantry?`)) return;

    fetch('/api/pantry/delete/', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify({ name: name })
    }).then(() => loadPantry());
}

// RECIPES
function getRecipes() {
    const list = document.getElementById('recipes-list');
    list.innerHTML = '<p>Calculating matches...</p>';

    fetch('/api/recipes/suggest/')
        .then(res => res.json())
        .then(data => {
            list.innerHTML = '';
            if(data.error || data.message || data.length === 0) {
                list.innerHTML = `<p>${data.error || data.message || "No matches found."}</p>`;
                return;
            }

            data.forEach(recipe => {
                const div = document.createElement('div');
                div.className = 'recipe-card';
                
                // Format Allergens
                let allergenHtml = '';
                if (recipe.allergens[0] !== "None") {
                    allergenHtml = `<span>⚠️ Contains: ${recipe.allergens.join(', ')}</span>`;
                }

                div.innerHTML = `
                    <h3>${recipe.title} <span>(${recipe.match_percentage}% Match)</span></h3>
                    <div>
                        <span>Difficulty: <strong>${recipe.difficulty}</strong></span>
                        ${allergenHtml}
                    </div>
                    <p><strong>You have:</strong> <span>${recipe.you_have.join(', ')}</span></p>
                    <p><strong>Missing:</strong> <span>${recipe.missing.join(', ')}</span></p>
                    <details>
                        <summary><strong>View Instructions</strong></summary>
                        <ol>
                            ${recipe.instructions.map(step => `<li>${step}</li>`).join('')}
                        </ol>
                    </details>
                    <hr>
                `;
                list.appendChild(div);
            });
        });
}

// Ingredient dropdown
const ingredientInput = document.getElementById('new-item-name');
const dropdownContainer = document.createElement('div');
dropdownContainer.id = 'ingredient-dropdown';
dropdownContainer.className = 'dropdown-list';
let dropdownOpen = false;

if (ingredientInput) {
    ingredientInput.parentElement.appendChild(dropdownContainer);
    
    ingredientInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        if (query.length < 2) {
            dropdownContainer.innerHTML = '';
            dropdownOpen = false;
            return;
        }
        
        fetch(`/api/ingredients/search/?q=${encodeURIComponent(query)}`)
            .then(res => res.json())
            .then(data => {
                dropdownContainer.innerHTML = '';
                if (data.length === 0) {
                    dropdownOpen = false;
                    return;
                }
                
                data.forEach(ingredient => {
                    const item = document.createElement('div');
                    item.className = 'dropdown-item';
                    item.textContent = ingredient;
                    item.onclick = function() {
                        ingredientInput.value = ingredient;
                        dropdownContainer.innerHTML = '';
                        dropdownOpen = false;
                    };
                    dropdownContainer.appendChild(item);
                });
                dropdownOpen = true;
            });
    });
    
    document.addEventListener('click', function(e) {
        if (e.target !== ingredientInput && !dropdownContainer.contains(e.target)) {
            dropdownContainer.innerHTML = '';
            dropdownOpen = false;
        }
    });
}

window.onload = loadPantry;