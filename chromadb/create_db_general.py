import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import spacy

nlp = spacy.load("en_core_web_sm")

# Load the Excel file
excel_file = "./docs/general_qnas.xlsx"  # Change this to your file path
df = pd.read_excel(excel_file)

# Initialize ChromaDB client (Persistent storage)
chroma_client = chromadb.PersistentClient(path="./general_chroma_db")

# Create or get a collection
collection = chroma_client.get_or_create_collection(name="qa_collection")

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def preprocess_query(query):
    doc = nlp(query) # Use spaCy for better tokenization
    tokens = [token.text for token in doc] #Extract text from tokens
    tokens.sort()
    return " ".join(tokens)  # Or join with any other separator

def store_questions():
    """Store questions and answers in ChromaDB."""
    for index, row in df.iterrows():
        question = str(row["Question"]).strip()
        answer = str(row["Answer"]).strip()
        question = preprocess_query(question)
        # print(question, question1)

        if question and answer:  # Ensure non-empty questions/answers
            embedding = embedding_model.encode(question).tolist()
            collection.add(
                ids=[f"q_{index}"],
                embeddings=[embedding],
                metadatas=[{"question": question, "answer": answer}]
            )
            print(f"Stored: {question}")


# Store the data
store_questions()
print("ChromaDB successfully stored questions and answers!")
