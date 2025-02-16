import os, set_env, pyodbc
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import streamlit as st
from PIL import Image
import streamlit as st
import spacy

# spaCy model load
nlp = spacy.load("en_core_web_sm")

#QnA maker
def initialize_azure_client():
    """Initialize Azure Language Studio QA client."""
    endpoint = str(os.getenv("endpoint"))
    credential = AzureKeyCredential(str(os.getenv("key")))
    return QuestionAnsweringClient(endpoint, credential)

client = initialize_azure_client()
project_name = os.getenv("knowledge_base_project")
deployment_name = os.getenv("deploymentName")

# Streamlit app
st.title("Simple Chatbot")
image = Image.open('./app_folder/onePal image.jpg')
st.sidebar.image(image, width=700)

print("====1=====", st.session_state)
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Set General context
if "context" not in st.session_state:
    st.session_state.context = "General"
if "context" in st.session_state and st.session_state.context == "My academic standing" and "have_student_id" not in st.session_state:
    st.session_state.have_student_id = False

if "context" in  st.session_state and st.session_state.context == "My academic standing" and not st.session_state.have_student_id:
    print("====2=====", st.session_state)
    v_student_id = st.text_input("Your student ID")
    if st.button("Submit"):
        st.session_state.student_id = v_student_id  # Store the value on submit
        st.session_state["have_student_id"] = True
        print("====3=====", st.session_state)
        with st.chat_message("assistant"):
            st.markdown("Got your student ID, what do you want to know ?")

# User input
user_input = st.chat_input("Say something ...")

# Handle user input
if user_input:
    print("session state:",st.session_state)
    print("context is:",st.session_state.context)
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if user_input.lower() == "my academic standing":
        st.session_state.context = "My academic standing"
        # Connect to database
        conn = pyodbc.connect(set_env.conn_str)
        print("Connected to SQL Server successfully!")
        cursor = conn.cursor()
        with st.chat_message("assistant"):
            st.markdown("What is your student ID ?")
        v_student_id = st.text_input("Your student ID")
        if st.button("Submit"):
            st.session_state.student_id = v_student_id  # Store the value on submit
            st.session_state["have_student_id"] = True

    # Get bot response
    if st.session_state.context == "My academic standing" and "have_student_id" in st.session_state and st.session_state.have_student_id:
        question = nlp(user_input)
        try:
            cursor.execute("SELECT TOP (10) [SchoolCalendarId],[CalendarName]  FROM [dbo].[Enrollment];")
        except:
            conn = pyodbc.connect(set_env.conn_str)
            print("Connected to SQL Server successfully!")
            cursor = conn.cursor()
            cursor.execute("SELECT TOP (10) [SchoolCalendarId],[CalendarName]  FROM [dbo].[Enrollment];")
        row = str(cursor.fetchone())
        print(row)
        response = "SQL server" + row
    elif st.session_state.context == "General":
        try:
            print("Closing DB connection")
            cursor.close()
            conn.close()
        except Exception as e:
            print("Error closing connection to SQL Server:", e)
        response = client.get_answers(question=user_input,project_name=project_name,deployment_name=deployment_name)
        response = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."

    # Display bot message
    try:
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    except Exception as e:
        print(e)
