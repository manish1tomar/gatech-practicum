from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
import asyncio, os, set_env

endpoint = "https://eastus.api.cognitive.microsoft.com/"
credential = str(os.environ.get('key'))
knowledge_base_project = "abc"
api_version="2021-10-01"
deploymentName="production"

client = QuestionAnsweringClient(endpoint, AzureKeyCredential(credential))

output = asyncio.run( client.get_answers(question="Hi"
                            , project_name=knowledge_base_project
                            , deployment_name=deploymentName)
             )

'''for candidate in output.answers:
    print("({}) {}".format(candidate.confidence, candidate.answer))
    print("Source: {}".format(candidate.source))
'''
print("A: {}".format(output.answers[0].answer))

asyncio.run(client.close())