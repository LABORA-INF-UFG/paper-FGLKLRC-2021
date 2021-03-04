import json

with open("stage_3_solution_T1_HCR1.json") as json_file:
    json_obj = json.load(json_file)
    solution = json_obj["Solution"]

    CU_count = [0, 0, 0]

    for item in solution:
        print(item)
        if item["CU_loc"] == 1 or item["CU_loc"] == 2:
            CU_count[0] += 1

        elif item["CU_loc"] == 3 or item["CU_loc"] == 4:
            CU_count[1] += 1
        else:
            CU_count[2] += 1

    print("[AG1, AG2, AC]")
    print(CU_count)