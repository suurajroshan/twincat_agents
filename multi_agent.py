# TODO: errors with using different models for the system and helper agents

import json
from bs4 import BeautifulSoup

from client import connect_to_twincat_server, disconnect_client
from utils import call_function
from tools import tool_list

from openai import OpenAI

class Dual_Agent_OPCUA:
    def __init__(self, 
                 api_key,
                 PROMPTS, # as a list, [SYSTEM_PROMPT, HELPER_PROMPT]
                 system_model="gpt-5", 
                 helper_model="gpt-5-mini-2025-08-07"):
        self.client = OpenAI(api_key=api_key)
        self.system_model = system_model
        self.helper_model = helper_model

        self.system_messages = [
            {"role": "developer", "content": PROMPTS[0]}
        ]

        self.helper_messages = [
            {"role": "developer", "content": PROMPTS[1]}
        ]

    def get_system_agent_response(self, user_input):
        self.system_messages.append(
            {"role": "user", "content": user_input}
        )

        response = self.client.responses.create(
            model = self.system_model,
            input = self.system_messages
        )

        self.system_messages.append(
            {"role": "assistant", "content": response.output_text}
        )

        return {"instruction_to_helper": response.output_text}

    def execute_helper_instruction(self, instruction):
        self.helper_messages.append(
            {"role": "user", "content": f"Execute this instruction: { instruction['instruction_to_helper'] }"}
        )

        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            response  = self.client.responses.create(
                model = self.helper_model,
                instructions="Direct instruction",
                tools = tool_list,
                input = self.helper_messages,
            )

            # filter out the reasoning type which cannot be handled for some smaller models
            filtered_output = []
            for i in response.output:
                if i.type != "reasoning":
                    filtered_output.append(i)
            self.helper_messages.append(
                {"role": "assistant", "content": filtered_output}
            )

            print(f"\nFunction calls: ")
            for i in response.output:
                if i.type != "function_call":
                    continue
                print(f"Name: {i.name}\nArgs: {i.arguments}")

            if any([i.type == "function_call" for i in response.output]):
                for tool_call in response.output:
                    if tool_call.type != "function_call":
                        continue

                    name = tool_call.name
                    args = json.loads(tool_call.arguments)

                    result = call_function(name, args)
                    print(f'Tool executed: {name}, Result: {result}')

                    print(self.helper_messages[2:])

                    self.helper_messages.append(
                        {"type": "function_call_output",
                        "call_id": tool_call.call_id,
                        "output": str(result)}
                    )
                    print(self.helper_messages[2:])
            else:
                print('response: ', response.output)
                return response.output
            
            iteration += 1

        return f"Helper agent exceeded maximum {max_iterations} iterations."
    
    def process_user_request(self, user_input):
        print(f"\n=== Processing User Request: {user_input} ===")

        try:
            connected = connect_to_twincat_server()
            print(f"Server connection: {connected}")
            
            while True:
                system_response = self.get_system_agent_response(user_input)
                print(f"\nSystem Agent Response: {system_response}")

                if "instruction_to_helper" in system_response:
                    print(f"\nExecuting via helper agent: {system_response['instruction_to_helper']}")
                    helper_result = self.execute_helper_instruction(system_response)
                    print(f"\nHelper Agent Result: {helper_result}")

                    feedback = f"""Helper Agent completed: '{system_response["instruction_to_helper"]}'\nResult: '{helper_result}'."""
                    user_input = feedback

                else:
                    print("No Instruction provided by System Agent.")
                    break

        finally:
            diconnected = disconnect_client()
            print(f"Server disconnected: {diconnected}")

if __name__ == "__main__":
        # TwinCAT code to pass as context
    codePath = './basicExampleXmlFile.xml'
    with open(codePath, 'r' , encoding='utf-8') as codeFile:
        codeFileData = codeFile.read()
    projectCode = BeautifulSoup(codeFileData, 'xml')

    # API Keys
    with open('secret_key', 'r') as k:
        key = k.read()

    # System Prompt
    with open('orchestrator_prompt.txt', 'r') as sp:
        SYSTEM_PROMPT = sp.read()
    SYSTEM_PROMPT += str(projectCode)

    with open('helper_agent_prompt.txt', 'r') as hp:
        HELPER_PROMPT = hp.read()

    opcua_system = Dual_Agent_OPCUA(
        api_key=key,
        PROMPTS=[SYSTEM_PROMPT, HELPER_PROMPT],
        system_model="gpt-5",      
        helper_model="gpt-5-mini",
    )
    
    # Process user request
    user_query = "What is the state of the motor?"
    opcua_system.process_user_request(user_query)
                    