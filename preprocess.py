import re
from pdfminer.high_level import extract_text
from nltk.corpus import stopwords
stop_words = stopwords.words('english')
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()


def clean_text(text):
  # Remove links
  text = re.sub('http.+', ' ', text) 

  # Remove mentions
  text = re.sub('@\w+', ' ', text)

  # Remove hashtags
  text = re.sub('#\w+', ' ', text)

  # Remove special characters
  text = re.sub('[^a-zA-Z]', ' ', text)

  # Remove multiple spaces, tabs, new lines
  text = re.sub('\s+', ' ', text)
  return text

def remove_stop_words(text):
  words = [word.lower() for word in text.split() if word.lower() not in stop_words]
  text = " ".join(words)
  return text

def lemmatization(text):
  words = [wnl.lemmatize(word) for word in text.split()]
  text = " ".join(words)
  return text

def preprocess_file(filename):
	text = extract_text('./static/resumes/' + filename)
	text = clean_text(text)
	text = remove_stop_words(text)
	text = lemmatization(text)

	return text

def preprocess_text(txt):
	text = clean_text(txt)
	text = remove_stop_words(text)
	text = lemmatization(text)

	return text