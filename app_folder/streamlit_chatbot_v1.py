import os, set_env, sqlServer
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import streamlit as st
from PIL import Image

image = Image.open('./app_folder/onePal image.jpg')

st.sidebar.image(image, width=700)

# Streamlit UI
st.title("🎓 GaDOE Chatbot - OnePal")
st.subheader("Howdy, ask me anything !!")

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your question here...")

def initialize_azure_client():
    """Initialize Azure Language Studio QA client."""
    endpoint = str(os.getenv("endpoint"))
    credential = AzureKeyCredential(str(os.getenv("key")))
    return QuestionAnsweringClient(endpoint, credential)

client = initialize_azure_client()
project_name = os.getenv("knowledge_base_project")
deployment_name = os.getenv("deploymentName")

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get bot response
    response = client.get_answers(
        question=user_input,
        project_name=project_name,
        deployment_name=deployment_name
    )

    response = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."

    # Display bot message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
