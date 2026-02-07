import unittest
import ollama
from model.model import clean_ingredient

def is_ollama_available():
    try:
        ollama.list()
        return True
    except:
        return False
    
class TestAIModel(unittest.TestCase):
    @unittest.skipUnless(is_ollama_available(), "Ollama unavailable, skipping AI model test")
    def test_clean_ingredient(self):
        """
        Verify that the model can identify and clean ingredient names from various raw input formats, while following the set rules.
        """
        test_cases = [
            ("bag of plain flour", "plain flour"),
            ("jar of smoked paprika", "smoked paprika"),
            ("pack of streaky bacon", "streaky bacon"),
            ("3 large onions", "onions"),
            ("punnet of strawberries", "strawberries"),
            ("bunch of coriander", "coriander"),
            ("bottle of olive oil", "olive oil"),
            ("tin of chopped tomatoes", "chopped tomatoes"),
            ("a massive tin of Heinz baked beans", "baked beans")
        ]
        
        for test_input, expected in test_cases:
            with self.subTest(raw_input=test_input):
                result = clean_ingredient(test_input)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()