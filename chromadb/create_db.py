import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Load the Excel file
excel_file = "./docs/abc_qnas.xlsx"  # Change this to your file path
df = pd.read_excel(excel_file)

# Initialize ChromaDB client (Persistent storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create or get a collection
collection = chroma_client.get_or_create_collection(name="qa_collection")

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def store_questions():
    """Store questions and answers in ChromaDB."""
    for index, row in df.iterrows():
        question = str(row["Question"]).strip()
        answer = str(row["Answer"]).strip()

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
