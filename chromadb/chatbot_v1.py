import chromadb, torch, set_env
from sentence_transformers import SentenceTransformer
from PIL import Image
import streamlit as st
import spacy, pyodbc
import pandas as pd

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
st.sidebar.subheader("You can ask about scholarships, dual enrollment, AP, my academic standing, graduation requirements, etc.")

if "context" not in st.session_state or st.session_state.context == "initial":
    print("loading database general")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="general")

if "context" in st.session_state and st.session_state.context == "scholarship":
    print("loading database scholarship")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="scholarship")

if "context" in st.session_state and st.session_state.context == "dual":
    print("loading database dual")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="dual")

if "context" in st.session_state and st.session_state.context == "academic standing":
    print("loading database general under context - academic standing")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="general")

if "context" in st.session_state and st.session_state.context == "gradreqs":
    print("loading database graduation requirements")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="gradreqs")

if "context" in st.session_state and st.session_state.context == "counselling":
    print("loading database counselling")
    chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
    collection = chroma_client.get_collection(name="counselling")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def query_chroma_db(query_text, top_k=1):
    """Queries ChromaDB with a question and returns the most relevant answer."""
    query_embedding = embedding_model.encode(query_text).tolist()
    results = collection.query( query_embeddings=[query_embedding], n_results=top_k )

    #print(results)
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

    q, a, dist = query_chroma_db(user_input)
    print("q.lower()", q.lower(), "dist", dist)

    if dist[0][0] <= 1:
        if q.lower() in ["dual", "ap", "advanced courses"]:
            st.session_state.context = "dual"
            print("Changed context to dual")
        elif q.lower() == "scholarships":
            st.session_state.context = "scholarship"
            print("Changed context to scholarship")
        elif q.lower() == "academic standing":
            st.session_state.context = "academic standing"
            print("Changed context to academic standing")
        elif q.lower() in ["graduation","graduation requirements"]:
            st.session_state.context = "gradreqs"
            print("Changed context to gradreqs")
        elif q.lower() == "counselling":
            st.session_state.context = "counselling"
            print("Changed context to counselling")

    if st.session_state.context == "academic standing" and "student_id" not in st.session_state and len([int(s) for s in user_input.split() if s.isdigit()]) > 0:
        st.session_state.student_id = [int(s) for s in user_input.split() if s.isdigit()][0]
        print(st.session_state.student_id)
        conn = pyodbc.connect(set_env.conn_str)
        print("Connected to SQL Server successfully!")
        cursor = conn.cursor()
        print("Executing SQL")
        #cursor.execute(f"select Subject, CreditsNeeded, EarnedCredit from [dbo].[Student_Credits] where StudentID in ( ${st.session_state.student_id} ) and Subject <> 'FL_ASL_CSE' order by StudentID asc, CreditsNeeded desc, Subject;")
        cursor.execute(f"SELECT *FROM[dbo].[vw_Student_Credits] WHERE StudentID in ( ${st.session_state.student_id} );")
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        a = pd.DataFrame.from_records(rows, columns=columns)
        a = a.reset_index(drop=True)
        print(type(a))
        cursor.close()
        conn.close()

    if dist[0][0] > 1 and st.session_state.context != "academic standing":
        chroma_client = chromadb.PersistentClient(path="./general_chroma_db")
        collection = chroma_client.get_collection(name="general")
        q, a, dist = query_chroma_db(user_input)
        print("q.lower()", q.lower(), "dist", dist)
        st.session_state.context = "initial"
        if dist[0][0] > 1.2:
            a = "Sorry, I'm still learning. You can ask like - scholarships, dual enrollment, AP, my academic standing, graduation requirements, etc."

    st.session_state.messages.append({"role": "assistant", "content": a})
    with st.chat_message("assistant"):
        if st.session_state.context == "academic standing" and isinstance(a, pd.DataFrame):
            st.markdown("Your academic standing is:")
            st.dataframe(a)
        else:
            st.markdown(a)
