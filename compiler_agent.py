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
                 PROMPTS, # as a list, [COMPILER_PROMPT, EXECUTOR_PROMPT]
                 compiler_model="gpt-5", 
                 executor_model="gpt-5-mini-2025-08-07"):
        self.client = OpenAI(api_key=api_key)
        self.compiler_model = compiler_model
        self.executor_model = executor_model
        self.executor_prompt = PROMPTS[1]

        self.compiler_messages = [
            {"role": "developer", "content": PROMPTS[0]}
        ]
        self.executor_messages = []

    def get_compiler_agent_response(self, compiler_user_prompt):
        self.compiler_messages.append(
            {"role": "user", "content": compiler_user_prompt}
        )

        response = self.client.responses.create(
            model = self.compiler_model,
            input = self.compiler_messages,
        )


        # print('Compiler agent reponse: \n', response.output_text)

        self.compiler_messages.append(
            {"role": "assistant", "content": response.output_text}
        )

        # with open('compiler_agent_output.txt', 'r', encoding="utf-8",) as f:
        #     cgo = f.read()

        self.executor_messages.append(
            {"role": "developer", "content": self.executor_prompt + '\n' + cgo}# response.output_text}
        )

        # print('Compiler agent response: \n', response.output_text)

    def execute_executor_instruction(self, user_prompt):
        self.executor_messages.append(
            {"role": "user", "content": user_prompt}
        )

        # print('executor model dev prompt: \n', self.executor_messages)

        max_iterations = 20
        iteration = 0

        # print('Executor messages: ', self.executor_messages[1:])

        while iteration < max_iterations:
            response  = self.client.responses.create(
                model = self.executor_model,
                tools = tool_list,
                input = self.executor_messages,
                parallel_tool_calls=False
            )

            # self.executor_messages.append({
            #     "role": "assistant", 
            #     "content": response.output
            # })

            print('Executor agent repsonse: \n', response)

            # filter out the reasoning type which cannot be handled for some smaller models
            filtered_output = []
            for i in response.output:
                if i.type != "reasoning":
                    filtered_output.append(i)
            self.executor_messages += response.output

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

                    self.executor_messages.append({
                            "type": "function_call_output",
                            "call_id": tool_call.call_id,
                            "output": str(result)
                    })
                    # print('executor messages: \n',self.executor_messages[2:])
            else:
                print('final response: ', response.output)
                return response.output
            
            iteration += 1

        return f"Executor agent exceeded maximum {max_iterations} iterations."
    
    def process_user_request(self, user_input):
        print(f"\n=== Processing User Request: {user_input} ===")

        try:
            connected = connect_to_twincat_server()
            print(f"Server connection: {connected}")

            compiler_response = self.get_compiler_agent_response('Compile the contextual knowledge as a prompt for the executor agent.')       
            # print(f"\nSystem Agent Response: {compiler_response}")
            
            output = self.execute_executor_instruction(user_input)
            print('final output', output)

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
    with open('compiler_prompt.txt', 'r') as cp:
        COMPILER_PROMPT = cp.read()
    COMPILER_PROMPT += str(projectCode)

    with open('executor_prompt.txt', 'r') as ep:
        EXECUTOR_PROMPT = ep.read()

    opcua_system = Dual_Agent_OPCUA(
        api_key=key,
        PROMPTS=[COMPILER_PROMPT, EXECUTOR_PROMPT],
        compiler_model="gpt-5",      
        executor_model="gpt-5-mini",
    )
    
    # Process user request
    user_query = "Increase the speed of the motor by 50%"
    opcua_system.process_user_request(user_query)
                    