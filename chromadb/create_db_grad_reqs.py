import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import spacy
import ollama

nlp = spacy.load("en_core_web_sm")

# Load the Excel file
excel_file = "./docs/gradreqs_qnas.xlsx"  # Change this to your file path
df = pd.read_excel(excel_file)

# Initialize ChromaDB client (Persistent storage)
chroma_client = chromadb.PersistentClient(path="./general_chroma_db")

# Create or get a collection
collection = chroma_client.get_or_create_collection(name="gradreqs")

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_question_variations(model, question, num_variations=10):
    variations = []
    for _ in range(num_variations):
        prompt = f"""Rephrase the following question in a different way, providing only the rephrased question:
        Original Question: {question}
        Rephrased Question: """
        try:
            response = ollama.chat(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            variation = response['message']['content'].strip()
            variations.append(variation)
        except Exception as e:
            print(f"Error generating variation: {e}")
            return variations
    return variations

def preprocess_query(query):
    doc = nlp(query) # Use spaCy for better tokenization
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct and not token.is_space] #Extract text from tokens
    tokens.sort()
    return " ".join(tokens)  # Or join with any other separator

def store_questions():
    """Store questions and answers in ChromaDB."""
    ollama_model = "llama2"
    existing_answers = set()

    # Fetch existing questions
    results = collection.get()
    if "metadatas" in results:
        for metadata in results["metadatas"]:
            existing_answers.add(metadata["answer"])

    for index, row in df.iterrows():
        question = str(row["Question"]).strip()
        answer = str(row["Answer"]).strip()

        # Skip if the question if answer already exists
        if answer in existing_answers and question not in ['What are the English courses I can take ?','What are the maths mathematics courses I can take ?','What are the science courses I can take ?','What are the social science courses I can take ?','What courses focus on world history ?','What courses focus on world studies ?','What courses focus on US history ?','ADDITIONAL COURSES THAT SATISFY THE THIRD SOCIAL SCIENCE UNIT','computer science courses that satisfy the foreign language/american sign language/computer science requirement']:
            print(f"{question} exists. Continuing with next...")
            continue

        question_variations = generate_question_variations(ollama_model, question)
        question_variations.append(question)

        if question_variations:
            embeddings = [embedding_model.encode(question).tolist()]
            metadatas = [{"question": question, "answer": answer}]
            ids = [f"q_{index}_{idx2}" for idx2 in range(len(question_variations)+1)]

            for variation in question_variations:
                q_v = preprocess_query(variation.replace("rephrased version of the original question:\n\n", ""))

                if q_v and answer:  # Ensure non-empty questions/answers
                    embeddings.append(embedding_model.encode(q_v).tolist())
                    metadatas.append({"question": q_v, "answer": answer})
            collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
            print(f"Stored: {metadatas}")

# Store the data
store_questions()
print("ChromaDB successfully stored questions and answers!")
