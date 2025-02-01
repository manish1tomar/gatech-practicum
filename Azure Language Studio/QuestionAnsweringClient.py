from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://eastus.api.cognitive.microsoft.com/"
credential = "BXWL0nYXpDhyohFV5MeZZf91tlSyHb3J34offV7UsSC5N3BX4OVIJQQJ99BAACYeBjFXJ3w3AAAaACOGs4uk"
knowledge_base_project = "Project-gatech"
api_version="2021-10-01"
deploymentName="production"

client = QuestionAnsweringClient(endpoint, credential)

output = client.get_answers(question="Hi", project_name=knowledge_base_project, deployment_name=deploymentName, api_version=api_version)

for candidate in output.answers:
    print("({}) {}".format(candidate.confidence, candidate.answer))
    print("Source: {}".format(candidate.source))
print("A: {}".format(output.answers[0].answer))