import re
from collections import Counter


class BagOfWords:
    def __init__(self):
        self.vocab: set[str] = set()
        self.vectors = []

    def preprocess(self, text):
        # Convert text to lowercase
        text = text.lower()
        # Remove punctuation using regex (keeps only word characters and whitespace)
        text = re.sub(r'[^\w\s]', '', text)
        # Split text into tokens (words)
        tokens = text.split()
        return tokens

    def bag_of_words(self, texts):
        tokenized_texts = []  # To store tokens for each text
        for text in texts:
            tokens = self.preprocess(text)
            tokenized_texts.append(tokens)
            self.vocab.update(*tokens)

        # Create a frequency vector for each document
        for tokens in tokenized_texts:
            counts = Counter(tokens)
            vector = [counts[word] for word in self.vocab]
            self.vectors.append(vector)
