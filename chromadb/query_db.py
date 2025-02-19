import chromadb
from sentence_transformers import SentenceTransformer
import timeit

start = timeit.default_timer()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./scholarship_dual_chroma_db")
collection = chroma_client.get_collection(name="qa_collection")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def query_chroma_db(query_text, top_k=1):
    """Queries ChromaDB with a question and returns the most relevant answer."""
    query_embedding = embedding_model.encode(query_text).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    if results["ids"][0]:  # Check if results exist
        for i, doc_id in enumerate(results["ids"][0]):
            answer = results["metadatas"][0][i].get("answer", "No answer found.")
            #print(f"\nAnswer:\n{answer}\n")
            #print("-" * 80)
    else:
        answer = "No relevant answers found."
        print("No relevant answers found.")
    return answer

print("Time took to load db :", timeit.default_timer() - start)

# Example Query
query_text = ["scholarship","schol", "hope", "zell", "mill", "gpa", "gpa zell", "gpa mill", "gpa hope", "elig hope", "elig zell", "elig mill", "eligibility hope", "eligibility zell", "eligibility mill"]
start = timeit.default_timer()
for query in query_text:
    print(query)
    print(query_chroma_db(query))
print("Time took to get answer is :", timeit.default_timer() - start)
