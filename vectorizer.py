from sklearn.feature_extraction.text import TfidfVectorizer

word_vectorizer = TfidfVectorizer(sublinear_tf=True, max_features=200)

def get_tfidf(docs):
	return word_vectorizer.fit_transform(docs).toarray()