import os, set_env, sqlServer
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import streamlit as st
from PIL import Image
import streamlit as st

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

# User input
user_input = st.chat_input("Say something ...")

# Handle user input
if user_input:
    print("context is:",st.session_state.context)
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if user_input.lower() == "my academic standing":
        st.session_state.context = "My academic standing"

    # Get bot response
    if st.session_state.context == "My academic standing":
        response = "SQL server"
    else:
        response = client.get_answers(question=user_input,project_name=project_name,deployment_name=deployment_name)
        response = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."

    # Display bot message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)