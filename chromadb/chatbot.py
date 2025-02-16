import os, pyodbc
from PIL import Image
import streamlit as st
import spacy

# spaCy model load
nlp = spacy.load("en_core_web_sm")

#QnA maker
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="qa_collection")

# Streamlit app
st.title("GaDOE chatbot - OnePal. Always there for you.")
image = Image.open('../app_folder/onePal image.jpg')
st.sidebar.image(image, width=700)

print("start session_state", st.session_state)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "context" not in st.session_state:
    st.session_state.context = "Initial"

if "options" not in st.session_state:
    st.session_state.options = False
elif st.session_state.options:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("My academic standing"):
            st.session_state.context = "My academic standing"
            with st.chat_message("assistant"):
                st.markdown("Lets talk about your academic standing.")
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

    with col2:
        if st.button("Scholarships"):
            st.session_state.context = "General"
            with st.chat_message("assistant"):
                st.markdown("Lets talk about scholarships.")
            response = client.get_answers(question="scholarships", project_name=project_name,deployment_name=deployment_name)
            response = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."

    with col3:
        if st.button("Graduation Requirements"):
            st.session_state.context = "General"
            with st.chat_message("assistant"):
                st.markdown("Lets talk about your graduation requirements.")
            response = client.get_answers(question="graduation requirements", project_name=project_name,deployment_name=deployment_name)
            response = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."

    st.session_state.options = False
    print("options updated to false after buttons")


    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

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

print("before user_input", st.session_state)

# User input
user_input = st.chat_input("Say something ...or just say Hi")
# Initial st loop returns from here

# Handle user input
if user_input and st.session_state.context == "Initial":
    st.session_state.options = True
    st.session_state.messages.append({"role": "user", "content": user_input})
    print("Printing Hi", st.session_state)
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        st.markdown("Hi, I'm onePal. Always happy to help. Click on any of below buttons to start.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("My academic standing"):
            st.session_state.context = "My academic standing"
            with st.chat_message("assistant"):
                st.markdown("Lets talk about your academic standing.")
    with col2:
        if st.button("Scholarships"):
            st.session_state.context = "General"
            with st.chat_message("assistant"):
                st.markdown("Lets talk about scholarships.")
    with col3:
        if st.button("Graduation Requirements"):
            st.session_state.context = "General"
            with st.chat_message("assistant"):
                st.markdown("Lets talk about your graduation requirements.")
    #st.session_state.options = False
    print("options given to user, option = True")
    #st.rerun()

elif user_input and st.session_state.context == "General":
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = client.get_answers(question=user_input,project_name=project_name,deployment_name=deployment_name)
    response = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."

elif user_input and st.session_state.context == "My academic standing":
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

# Display bot message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
