import json

# TODO: check if the dynamically assigned tools as be included in __init__.py

with open('tools/get_root_object_node.json', 'r') as f:
    get_root_object_node = json.loads(f.read())

with open('tools/get_children_of_nodes.json', 'r') as f:
    get_children_of_nodes = json.loads(f.read())

with open('tools/get_node_value.json', 'r') as f:
    get_node_value = json.loads(f.read())

with open('tools/write_value_to_node.json', 'r') as f:
    write_value_to_node = json.loads(f.read())