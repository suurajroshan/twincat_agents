import client

from inspect import getmembers, isfunction

def call_function(name, args):
    try:
        if any([m[0] == name for m in getmembers(client, isfunction)] ):
            function_to_call = getattr(__import__("client"), name)
            return function_to_call(**args)
    
    except Exception as e:
        print(f"Error while calling the function. Exception occured: {e}")
        return f"Exception occured: {e}"
    
if __name__ == "__main__":
    try:
        func_name = "connect_to_twincat_server"
        print(call_function(func_name, {}))
    finally:
        func_name = "disconnect_client"
        print(call_function(func_name, {}))
    