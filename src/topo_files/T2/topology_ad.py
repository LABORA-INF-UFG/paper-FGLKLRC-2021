import json

with open("256_CRs_links_LC.json") as json_file:
    json_obj = json.load(json_file)

    links = json_obj["links"]

    for l in links:
        if l["toNode"] < l["fromNode"]:
            temp = l["toNode"]
            l["toNode"] = l["fromNode"]
            l["fromNode"] = temp

    count = 0
    for l in links:
        ############ ENTRE 3 E 4 ###################
        for i in range(23, 43):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 3
                    count = 1
                else:
                    l["fromNode"] = 4
                    count = 0

        ############ ENTRE 5 E 6 ###################
        for i in range(43, 63):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 5
                    count = 1
                else:
                    l["fromNode"] = 6
                    count = 0
        ############ ENTRE 7 E 8 ###################
        for i in range(63, 83):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 7
                    count = 1
                else:
                    l["fromNode"] = 8
                    count = 0

        ############ ENTRE 9 E 10 ###################
        for i in range(83, 103):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 9
                    count = 1
                else:
                    l["fromNode"] = 10
                    count = 0

        ############ ENTRE 11 E 12 ###################
        for i in range(103, 123):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 11
                    count = 1
                else:
                    l["fromNode"] = 12
                    count = 0

        ############ ENTRE 13 E 14 ###################
        for i in range(123, 143):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 13
                    count = 1
                else:
                    l["fromNode"] = 14
                    count = 0

        ############ ENTRE 15 E 16 ###################
        for i in range(143, 163):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 15
                    count = 1
                else:
                    l["fromNode"] = 16
                    count = 0

        ############ ENTRE 17 E 18 ###################
        for i in range(163, 183):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 17
                    count = 1
                else:
                    l["fromNode"] = 18
                    count = 0

        ############ ENTRE 19 E 20 ###################
        for i in range(183, 203):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 19
                    count = 1
                else:
                    l["fromNode"] = 20
                    count = 0

        ############ ENTRE 21 E 22 ###################
        for i in range(203, 223):
            if l["toNode"] == i:
                if count == 0:
                    l["fromNode"] = 21
                    count = 1
                else:
                    l["fromNode"] = 22
                    count = 0

    print("############# ENTRE 3 e 4 ##############")
    for l in links:
        if l["toNode"] in range(23, 43):
            print(l)

    print("############# ENTRE 5 e 6 ##############")
    for l in links:
        if l["toNode"] in range(43, 63):
            print(l)

    print("############# ENTRE 7 e 8 ##############")
    for l in links:
        if l["toNode"] in range(63, 83):
            print(l)

    print("############# ENTRE 9 e 10 ##############")
    for l in links:
        if l["toNode"] in range(83, 103):
            print(l)

    print("############# ENTRE 11 e 12 ##############")
    for l in links:
        if l["toNode"] in range(103, 123):
            print(l)

    print("############# ENTRE 13 e 14 ##############")
    for l in links:
        if l["toNode"] in range(123, 143):
            print(l)

    print("############# ENTRE 15 e 16 ##############")
    for l in links:
        if l["toNode"] in range(143, 163):
            print(l)

    print("############# ENTRE 17 e 18 ##############")
    for l in links:
        if l["toNode"] in range(163, 183):
            print(l)

    print("############# ENTRE 19 e 20 ##############")
    for l in links:
        if l["toNode"] in range(183, 203):
            print(l)

    print("############# ENTRE 21 e 22 ##############")
    for l in links:
        if l["toNode"] in range(203, 223):
            print(l)

with open("256_CRs_links_LC.json", "w") as json_new_file:
    json.dump(json_obj, json_new_file)