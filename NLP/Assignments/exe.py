# import sys
# print(sys.executable)
# import spacy
# nlp = spacy.load("en_core_web_sm")
# print("SpaCy works ✅")


# from nltk.tokenize import word_tokenize, sent_tokenize
# text = "Hi there! I'm testing tokens. Let's see how it works."
# sentences=sent_tokenize(text)
# print(sentences)
# tokens = [word_tokenize(s) for s in sentences]
# print(tokens)

# import spacy
# nlp = spacy.load("en_core_web_sm")
# doc = nlp("Can you schedule a meeting for tomorrow morning?")
# for token in doc:
#     print(token.text, token.pos_)

# Example of stemming vs. lemmatization with NLTK and spaCy

# from nltk.stem import PorterStemmer
# from nltk.stem import WordNetLemmatizer
# import spacy

# ps = PorterStemmer()
# lemmatizer = WordNetLemmatizer()
# nlp = spacy.load("en_core_web_sm")

# word = "running"

# print(ps.stem(word))                  # running -> run
# print(lemmatizer.lemmatize(word, pos='v'))   # running -> run

# doc = nlp("better")
# for token in doc:
#     print(token.text, token.lemma_)   # better -> good



import spacy
import re

nlp = spacy.load("en_core_web_sm")

text = "Hello!!! Can you PLEASE tell me my order-status????😀"

# 1. Lowercase
text_lower = text.lower()
print("After lowercasing:", text_lower)

# 2. Remove noise
text_clean = re.sub(r'[^a-z\s-]', '', text_lower)
print("After noise removal:", text_clean)

# 3. Tokenization
doc = nlp(text_clean)
tokens = [token.text for token in doc]
print("Tokens:", tokens)

# 4. Normalization (remove hyphens)
normalized_tokens = [token.replace('-', '') for token in tokens if token.replace('-', '') != '']
print("Normalized Tokens:", normalized_tokens)

# 5. Lemmatization
lemmatized_tokens = [nlp(token)[0].lemma_ for token in normalized_tokens]
print("Lemmatized Tokens:", lemmatized_tokens)

# 6. Final Words
final_words = lemmatized_tokens
print("Final Words:", final_words)
