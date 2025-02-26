import chromadb, torch
from sentence_transformers import SentenceTransformer
from PIL import Image
import streamlit as st
import spacy

torch.classes.__path__ = []

# Load a spaCy model (or use a simpler tokenizer)
nlp = spacy.load("en_core_web_sm") # or whatever model you want to use

def preprocess_query(query):
    doc = nlp(query) # Use spaCy for better tokenization
    tokens = [token.text for token in doc] #Extract text from tokens
    tokens.sort()
    return " ".join(tokens)  # Or join with any other separator

# Streamlit app
st.title("FCS chatbot - Guidance Genie. Happy to help.")
image = Image.open('./Virtual_Guidance_Genie.jpg')
st.sidebar.image(image, width=700)
st.sidebar.header("Guidance Genie here, Where students come first !!")
st.sidebar.subheader("You can ask about scholarships, dual enrollment, my academic standing, graduation requirements, etc.")

if "context" not in st.session_state or st.session_state.context == "initial":
    print("loading database general")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="general")

if "context" in st.session_state and st.session_state.context == "scholarship":
    print("loading database scholarship dual")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="scholarship")

if "context" in st.session_state and st.session_state.context == "dual":
    print("loading database scholarship dual")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="dual")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("start session_state", st.session_state)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def query_chroma_db(query_text, top_k=1):
    """Queries ChromaDB with a question and returns the most relevant answer."""
    query_embedding = embedding_model.encode(query_text).tolist()
    results = collection.query( query_embeddings=[query_embedding], n_results=top_k )

    print(results)
    if results["ids"][0]:  # Check if results exist
        for i, doc_id in enumerate(results["ids"][0]):
            answer = results["metadatas"][0][i].get("answer", "No answer found.")
            question = results["metadatas"][0][i].get("question", "No question found.")
    else:
        answer = "No relevant answers found."
        question = "No question found."
    return question, answer, results['distances']

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "context" not in st.session_state:
    st.session_state.context = "initial"

user_input = st.chat_input("Say something ...or just say Hi")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    user_input = preprocess_query(user_input)
    print(user_input)
    q, a, dist = query_chroma_db(user_input)
    print(q,"\n", a, "\n", dist)
    if q.lower() == "dual":
        st.session_state.context = "dual"
    elif q.lower() == "scholarships":
        st.session_state.context = "scholarship"

    if dist[0][0] > 1:
        chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
        collection = chroma_client.get_collection(name="general")
        q, a, dist = query_chroma_db(user_input)
        st.session_state.context = "initial"
        if dist[0][0] > 1:
            a = "Sorry, I'm still learning. You can ask like - scholarships, dual enrollment, my academic standing, graduation requirements, etc."

    st.session_state.messages.append({"role": "assistant", "content": a})
    with st.chat_message("assistant"):
        st.markdown(a)
