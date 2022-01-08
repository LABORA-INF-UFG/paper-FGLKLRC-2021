import json

with open("256_CRs_nodes_LC.json") as json_file:
    json_obj = json.load(json_file)
    nodes = json_obj["nodes"]

    print(nodes)

    for i in range(129, 257):
        new_node = {}

        new_node["nodeNumber"] = i
        new_node["cpu"] = 8
        new_node["RU"] = 1

        nodes.append(new_node)

    print(nodes)

with open("256_CRs_nodes_LC.json", "w") as json_new_file:
    json.dump(json_obj, json_new_file)