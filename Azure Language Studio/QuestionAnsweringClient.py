from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://{myaccount}.api.cognitive.microsoft.com"
credential = AzureKeyCredential("{api-key}")

client = QuestionAnsweringClient(endpoint, credential)