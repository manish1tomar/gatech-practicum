from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

endpoint = "https://language-gatech.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=Project-gatech&api-version=2021-10-01&deploymentName=production"
credential = AzureKeyCredential("BXWL0nYXpDhyohFV5MeZZf91tlSyHb3J34offV7UsSC5N3BX4OVIJQQJ99BAACYeBjFXJ3w3AAAaACOGs4uk")

client = AuthoringClient(endpoint, credential)