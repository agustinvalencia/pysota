from sklearn.feature_extraction.text import CountVectorizer


class FrequencyCounter:
    def __init__(self):
        self.vectorizer = CountVectorizer()

    def fit_transform(self, texts):
        return self.vectorizer.fit_transform(texts)
