########## CLIENT ##########
from typing import Union

from opcua import Client, ua
from opcua.ua.uaerrors import UaStatusCodeError

url = "opc.tcp://DESKTOP-P1S5I92:4840"
UA_client = Client(url)
UA_client.set_user("admin")
UA_client.set_password("admin")

# def get_node_children(client = UA_client) -> str:
#     node = UA_client.get_node("ns=1;s=PLC1")
#     for n in node.get_children():

def get_children_of_nodes(NodeId: str, client=UA_client) -> str:
    """
    Retrieve and list the immediate child nodes of a given OPC UA node.

    Args:
        NodeId (str): The NodeId of the parent OPC UA node to browse. 
                      This can be in string format such as 'ns=4;s=MAIN'.
        client (opcua.Client, optional): An active OPC UA client instance. 
                                         Defaults to the global UA_client.

    Returns:
        str: A formatted string where each line contains the child node's 
             NodeId and its browse name.
    """
    try:
        node = client.get_node(NodeId)
        out_string = f""
        for child in node.get_children():
            out_string += f"""Child NodeId: "{child}", Child Name: "{child.get_browse_name()}".\n"""
        if out_string == "":
            raise Exception("No children for this node.")
        return out_string
    except Exception as e:
        return f"""Error getting the children of node. Exception raised: "{str(e)}" """

def get_root_object_node(client=UA_client) -> str:
    """
    Retrieve the OPC UA server's root 'Objects' node.

    Args:
        client (opcua.Client, optional): An active OPC UA client instance. 
                                         Defaults to the global UA_client.

    Returns:
        str: A formatted string containing the NodeId of the root 'Objects' node.
    """
    try:
        obj = UA_client.get_objects_node()
        return f"""Root object NodeId: "{obj}".\n"""
    except Exception as e:
        return f"""Error getting the root object node. Exception raised: "{str(e)}" """


def connect_to_twincat_server(client=UA_client) -> str:
    """
    Connect to a TwinCAT OPC UA server.

    Args:
        client (opcua.Client, optional): An OPC UA client instance configured 
                                         with the target server's endpoint and credentials.
                                         Defaults to the global UA_client.

    Returns:
        str: A message indicating whether the connection succeeded or failed.
    """
    try:
        client.connect()
        return f"Connected to the OPC UA Server."
    except Exception as e:
        return f"Error connecting to the server. Exception raised: {str(e)}"

def disconnect_client(client = UA_client) -> str:
    """
    Disconnect the OPC UA client from the server.

    Args:
        client (opcua.Client, optional): The OPC UA client instance to disconnect.
                                         Defaults to the global UA_client.

    Returns:
        str: A message indicating whether the disconnection succeeded or failed.
    """
    try:
        client.disconnect()
        return f"Client disconnected."
    except Exception as e:
        return f"Error disconnecting server. Exception raised: {str(e)}"
    
def get_node_value(NodeId: str, client=UA_client) -> Union[str, bool, float, int]:
    """
    Retrieve the value of a node from the connected OPC UA server.

    This function fetches the node corresponding to the given NodeId
    from the provided OPC UA client and returns its current value.

    Args:
        NodeId (str): The NodeId of the target node in the OPC UA server address space.
        client (opcua.Client, optional): An instance of an active OPC UA client. Defaults to the global `UA_client`.

    Returns:
        str | bool | float | int: The value stored in the node, which may be of various data types depending on the server configuration.
    """
    node = client.get_node(NodeId)
    value = node.get_value()
    return value

def write_value_to_node(NodeId: str, value: Union[float, bool], client=UA_client) -> str:
    """
    Write a value to a specified OPC UA node.

    This function connects to the given node on the OPC UA server using the provided client,
    determines the appropriate VariantType for the given Python value, and writes it to the node.

    Args:
        NodeId (str): The NodeId of the target node in the OPC UA server address space.
        value (int | float | bool): The value to write to the node. Currently supports Boolean and Float types.

    Returns:
        str: A confirmation message indicating the value has been written.
    """
    try:
        if type(value) == bool:
            datatype = ua.VariantType.Boolean
        if type(value) == float:
            datatype = ua.VariantType.Float
        node = client.get_node(NodeId)
        node.set_value(ua.DataValue(ua.Variant(value, datatype)))
        # node.set_attribute(ua.AttributeIds.Value, ua.DataValue(trueVariant))
        return f"Node value has been set to {get_node_value(NodeId)}."
    except Exception as e:
        return f"""Error writing value to node. Exception raised: "{str(e)}" """
    except:
        return f"Error"

if __name__ =="__main__":
    try:
        UA_client.connect()
        print("✅ Connected to OPC UA Server!")

        a = get_node_value("ns=4;s=MAIN.GreenToggle")
        import json
        args = json.loads('{"NodeId":"ns=4;s=MAIN.BlueToggle","value":true}')
        b = write_value_to_node(**args)
        print(b)
        # a = UA_client.get_node("ns=1;s=PLC1")
        # for aa in a.get_children():
        #     print(aa, aa.get_browse_name())

    #    # Access variable nodes
    #     green_toggle = UA_client.get_node("ns=4;s=MAIN.GreenToggle")
    #     blue_toggle = UA_client.get_node("ns=4;s=MAIN.BlueToggle")
    #     yellow_toggle = UA_client.get_node("ns=4;s=MAIN.YellowToggle")
    #     motor_toggle = UA_client.get_node("ns=4;s=MAIN.MotorToggle")

    #     # ✅ READ values
    #     print("🔎 Reading values:")
    #     print("GreenToggle:", green_toggle.get_value())
    #     print("BlueToggle:", blue_toggle.get_value())
    #     print("YellowToggle:", yellow_toggle.get_value())
    #     print("MotorToggle:", motor_toggle.get_value())

    #     # trueVariant = ua.Variant(1) # , ua.VariantType.Boolean)
    #     # green_toggle.set_attribute(ua.AttributeIds.Value, ua.DataValue(trueVariant))

    #     # ✅ WRITE values
    #     # print("✏️ Writing values:")
    #     # green_toggle.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))   # Turn ON
    #     # blue_toggle.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))  # Turn OFF

    #     print("✅ Updated values:")
    #     print("GreenToggle (new):", green_toggle.get_value())
    # #     print("BlueToggle (new):", blue_toggle.get_value())

    # except Exception as e:
    #     print("❌ Error:", e)

    finally:
        UA_client.disconnect()
        print("🔌 Disconnected")

