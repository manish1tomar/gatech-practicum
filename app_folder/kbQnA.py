import os, set_env
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient


def initialize_client():
    """Initialize Azure Language Studio QA client."""
    endpoint = str(os.getenv("endpoint"))
    #credential = DefaultAzureCredential()
    credential = AzureKeyCredential(str(os.getenv("key")))
    return QuestionAnsweringClient(endpoint, credential)


def ask_knowledge_base(client, question, project_name, deployment_name):
    """Query Azure AI Language Studio knowledge base."""
    response = client.get_answers(
        question=question,
        project_name=project_name,
        deployment_name=deployment_name
    )
    if response.answers:
        return response.answers[0].answer
    return "Sorry, I couldn't find an answer to that."


def chatbot():
    """Simple chatbot loop."""
    client = initialize_client()
    project_name = str(os.getenv("knowledge_base_project"))
    deployment_name = str(os.getenv("deploymentName"))

    print("Azure Knowledge Base Chatbot. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = ask_knowledge_base(client, user_input, project_name, deployment_name)
        print("Bot:", response)


# if __name__ == "__main__":
#     chatbot()
