# SmartRecipe API Documentation

**URL:** `https://smartrecipeapi-cqeaf6chh5endhan.francecentral-01.azurewebsites.net`  
**Authentication:** The API relies on Django Session Authentication and requires a valid `X-CSRFToken` in the headers for all `POST`, `PUT`, and `DELETE` requests.

---

## 1. Authentication & Account Management

### 1.1 Register User
* **Endpoint:** `/api/register/`
* **Method:** `POST`
* **Authentication:** None
* **Description:** Creates a new user account.
* **Request Body:**
  ```json
  {
    "username": "bob123",
    "password": "password123",
    "first_name": "Bob",
    "last_name": "Smith",
    "email": "bob.smith@example.com"
  }
  ```
* **Responses:**
  * `201 Created`: `{"Success": "User registered successfully"}`
  * `400 Bad Request`: `{"Error": "All fields are required"}` / `{"Error": "Username already exists"}`

### 1.2 Login User
* **Endpoint:** `/api/login/`
* **Method:** `POST`
* **Authentication:** None 
* **Description:** Authenticates a user and starts a session.
* **Request Body:**
  ```json
  {
    "username": "bob123",
    "password": "password123"
  }
  ```
* **Responses:**
  * `200 OK`: `{"Success": "Logged in successfully"}`
  * `400 Bad Request`: `{"Error": "Incorrect username or password"}`

### 1.3 Logout User
* **Endpoint:** `/api/logout/`
* **Method:** `POST`
* **Authentication:** Session required
* **Description:** Ends the current user session.
* **Responses:**
  * `200 OK`: `{"Success": "Logged out successfully"}`

### 1.4 Update Account
* **Endpoint:** `/api/account/update/`
* **Method:** `POST`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Updates the authenticated user's username or password.
* **Request Body:** *(All fields optional but validated if provided)*
  ```json
  {
    "new_username": "bob99",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
  }
  ```
* **Responses:**
  * `200 OK`: `{"success": "Account updated successfully"}`
  * `400 Bad Request`: `{"error": "Passwords do not match"}` / `{"error": "Username already taken"}`

---

## 2. Pantry Management

### 2.1 Get Pantry
* **Endpoint:** `/api/pantry/`
* **Method:** `GET`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Retrieves all ingredients currently stored in the user's pantry.
* **Responses:**
  * `200 OK`:
    ```json
    [
      {
        "name": "milk",
        "quantity": "2 Liters"
      },
      {
        "name": "carrot",
        "quantity": "500g"
      }
    ]
    ```

### 2.2 Add to Pantry
* **Endpoint:** `/api/pantry/add/`
* **Method:** `POST`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Adds an existing ingredient to the user's pantry.
* **Request Body:**
  ```json
  {
    "name": "milk"
  }
  ```
* **Responses:**
  * `201 Created`: `{"message": "milk added to pantry"}`
  * `200 OK`: `{"message": "milk is already in pantry"}`
  * `400 Bad Request`: `{"error": "Ingredient 'unknown_item' not recognized"}`

### 2.3 Update Pantry Item
* **Endpoint:** `/api/pantry/update/`
* **Method:** `PUT`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Updates the quantity of a specific ingredient in the user's pantry.
* **Request Body:**
  ```json
  {
    "name": "milk",
    "quantity": "1 Gallon"
  }
  ```
* **Responses:**
  * `200 OK`: `{"message": "milk quantity updated to 1 Gallon"}`
  * `400 Bad Request`: `{"error": "Name and quantity are required"}`
  * `404 Not Found`: `{"error": "milk not found in pantry"}`

### 2.4 Delete Pantry Item
* **Endpoint:** `/api/pantry/delete/`
* **Method:** `DELETE`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Removes an ingredient entirely from the user's pantry.
* **Request Body:**
  ```json
  {
    "name": "milk"
  }
  ```
* **Responses:**
  * `200 OK`: `{"message": "milk removed from pantry"}`
  * `404 Not Found`: `{"error": "milk not found in pantry"}`

---

## 3. Ingredients & Recipes

### 3.1 Search Ingredients
* **Endpoint:** `/api/ingredients/search/`
* **Method:** `GET`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Autocomplete endpoint that returns up to 50 matching ingredients based on a query.
* **Query Parameters:** `?q=<search_string>` (Requires minimum 2 characters)
* **Responses:**
  * `200 OK`:
    ```json
    [
      "carrot",
      "carrot cake",
      "baby carrot"
    ]
    ```

### 3.2 Suggest Recipes
* **Endpoint:** `/api/recipes/suggest/`
* **Method:** `GET`
* **Authentication:** Session required (`IsAuthenticated`)
* **Description:** Suggests recipes based on the ingredients in the user's pantry. Results are scored based on the number of matching items and return missing ingredients alongside allergen warnings.
* **Query Parameters:** `?limit=<int>` (Optional, defaults to 10)
* **Responses:**
  * `200 OK`:
    ```json
    [
      {
        "id": 1423,
        "title": "carrot and minced beef stew",
        "difficulty": "Medium",
        "allergens": ["dairy", "wheat"],
        "match_percentage": 66.67,
        "you_have": ["carrot", "minced beef"],
        "missing": ["beef broth"],
        "instructions": [
          "chop the carrots",
          "brown the minced beef",
          "simmer with broth"
        ]
      }
    ]
    ```