from bs4 import BeautifulSoup
import json
from client import connect_to_twincat_server, disconnect_client

from openai import OpenAI

from tools import tool_list
from utils import call_function

# TwinCAT code to pass as context
codePath = './basicExampleXmlFile.xml'
with open(codePath, 'r' , encoding='utf-8') as codeFile:
    codeFileData = codeFile.read()
projectCode = BeautifulSoup(codeFileData, 'xml')

# API Keys
with open('secret_key', 'r') as k:
    key = k.read()

# System Prompt
with open('system_agent_prompt.txt', 'r') as sp:
    SYSTEM_PROMPT = sp.read()
SYSTEM_PROMPT += str(projectCode)

with open('helper_agent_prompt.txt', 'r') as hp:
    HELPER_PROMPT = hp.read()

client = OpenAI(api_key=key)

messages = [
    {
        "role": "developer",
        "content": f"{SYSTEM_PROMPT}"
    },
    {
        "role": "user",
        "content": "The variable `GreenLight` is it both readable and writable?"
    }
]

try: 
    connected = connect_to_twincat_server()
    print(connected)

    while True:
        response = client.responses.create(
            model="gpt-4.1-mini",
            tools=tool_list,
            input=messages,
        )
        
        for event in response:
            if event[0] == 'tools':
                continue
            print(event)

        function_call = None
        function_call_arguments = None
        messages += response.output

        if any([i.type == "function_call" for i in response.output]):
            for tool_call in response.output:
                if tool_call.type != "function_call":
                    continue

                name = tool_call.name
                args = json.loads(tool_call.arguments)

                result = call_function(name, args)
                print('Result: ', result)
                messages.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result)
                })
        else:
            break

    print(response.output_text)

finally:
    disconnected = disconnect_client()
    print(disconnected)
