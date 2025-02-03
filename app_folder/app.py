from flask import Flask, request, jsonify
import os, set_env
#import kbQnA
from flask_cors import CORS  # Enable CORS for frontend requests
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

def initialize_client():
    """Initialize Azure Language Studio QA client."""
    endpoint = str(os.getenv("endpoint"))
    #credential = DefaultAzureCredential()
    credential = AzureKeyCredential(str(os.getenv("key")))
    return QuestionAnsweringClient(endpoint, credential)

client = initialize_client()
project_name = os.getenv("knowledge_base_project")
deployment_name = os.getenv("deploymentName")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    response = client.get_answers(
        question=question,
        project_name=project_name,
        deployment_name=deployment_name
    )

    answer = response.answers[0].answer if response.answers else "Sorry, I couldn't find an answer."
    return jsonify({"response": answer})

if __name__ == '__main__':
    app.run(debug=True)
