import spacy

nlp = spacy.load("en_core_web_sm")  # Or a larger model like "en_core_web_trf"

def extract_important_words(text):
    doc = nlp(text)
    important_words = []

    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:  # Remove stop words, punctuation, and spaces
            important_words.append(token.lemma_.lower())  # Use lemma (base form) and lowercase

    return important_words

text = "What is the GPA requirement to maintain the Zell Miller Scholarship?"
important_words = extract_important_words(text)
print(important_words)  # Output: ['scholarship', 'available']


# More advanced filtering (optional):
def extract_important_words_advanced(text):
    doc = nlp(text)
    important_words = []

    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:
            if token.pos_ in ["NOUN", "PROPN", "ADJ"]: # Keep only nouns, proper nouns, and adjectives (you can customize this)
                important_words.append(token.lemma_.lower())
            elif token.pos_ == "VERB" and token.lemma_ not in ["be", "have"]: # Include verbs but exclude common helping verbs like 'be' and 'have'
                important_words.append(token.lemma_.lower())

    return important_words

important_words_advanced = extract_important_words_advanced(text)
print(important_words_advanced) # Output: ['scholarship', 'available']


# Even more advanced filtering (optional):
# Using dependency parsing to identify the core subject and object
def extract_core_words(text):
    doc = nlp(text)
    core_words = []

    for token in doc:
        if token.dep_ in ["nsubj", "dobj", "ROOT"]: # Subject, direct object, and root of the sentence
            if not token.is_stop and not token.is_punct and not token.is_space:
                 core_words.append(token.lemma_.lower())

    return core_words

core_words = extract_core_words(text)
print(core_words) # Output: ['scholarship']