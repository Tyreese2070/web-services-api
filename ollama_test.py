import ollama

def normalize_ingredient(user_input):
    response = ollama.chat(
        model="llama3",
        messages=[
            {
                'role': 'user',
                'content': f"Extract the main food ingredient from this text: '{user_input}'. Return ONLY the ingredient name in lowercase."
            },
        ]
    )
    return response['message']['content'].strip()

print(normalize_ingredient("leftover roast chicken from yesterday"))

## Check "baked beans" only returns "beans"