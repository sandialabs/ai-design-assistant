
import os
from openai import OpenAI
import json
import pathlib
path_to_here = pathlib.Path(__file__).parent.resolve()

# https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models
# https://platform.openai.com/docs/guides/function-calling?lang=python
# https://platform.openai.com/docs/guides/fine-tuning/fine-tuning-examples

def sendToOpenAI(ipt, functionData = None, model="gpt-4o"):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        organization=os.environ.get("OPENAI_ORG"),
    )

    if functionData is None:
        raise ValueError('Did not recieve any function data')


    tools = [{"type":"function","function":v} for v in functionData]

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "assistant",
                # "content": "Always return your best guess as to the function being called.  Do not respond to the user or ask a question under any circumstances.  Your only role is to map the input to the appropriate function from the list you have been provided with",
                "content": "Always output your response by using a tool.  Do not respond to the user or ask a question under any circumstances.", 
            },
            {
                "role": "user",
                "content": ipt,
            }
        ],
        model = model,
        tools=tools,
    )

    return chat_completion
