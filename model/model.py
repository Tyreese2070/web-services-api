import ollama

# Change to alternative recipe suggestion AI

def clean_ingredient(raw_input):
    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                # Define task and rules
                {'role': 'system', 'content': "You are a strict data cleaner. Output ONLY the food ingredient name in lowercase. No punctuation."},
                
                # Fake history to teach the pattern
                {'role': 'user', 'content': "a massive tin of Heinz baked beans"},
                {'role': 'assistant', 'content': "baked beans"},
                
                {'role': 'user', 'content': "tub of vanilla ice cream"},
                {'role': 'assistant', 'content': "vanilla ice cream"},
                
                {'role': 'user', 'content': "bag of frozen garden peas"},
                {'role': 'assistant', 'content': "garden peas"},
                
                {'role': 'user', 'content': raw_input}
            ],
            # speed up response by reducing creativity and limiting output length
            options={
                "temperature": 0,
                "num_predict": 10,
            },
            keep_alive=-1
        )
        return response['message']['content'].strip().lower()
    except Exception as e:
        return f"Error: {str(e)}"