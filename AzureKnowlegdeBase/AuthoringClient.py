from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import AuthoringClient

endpoint = "https://language-gatech.cognitiveservices.azure.com/language/:query-knowledgebases?projectName=Project-gatech&api-version=2021-10-01&deploymentName=production"
credential = AzureKeyCredential("")

client = AuthoringClient(endpoint, credential)
