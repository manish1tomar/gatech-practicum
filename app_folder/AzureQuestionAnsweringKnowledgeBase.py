from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.aio import QuestionAnsweringClient
import asyncio, os, set_env

async def getAnswer(question="Hi"):
    endpoint = "https://eastus.api.cognitive.microsoft.com/"
    credential = str(os.environ.get('key'))
    knowledge_base_project = "abc"
    api_version="2021-10-01"
    deploymentName="production"

    client = QuestionAnsweringClient(endpoint, AzureKeyCredential(credential))

    output = await client.get_answers(question=question
                                , project_name=knowledge_base_project
                                , deployment_name=deploymentName)


    #print("A: {}".format(output.answers[0].answer))

    await client.close()
    return output.answers[0].answer