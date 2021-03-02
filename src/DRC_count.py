import json

with open("stage_3_solution_T1_HCF1.json") as solution_file:
    json_obj = json.load(solution_file)
    solution = json_obj["Solution"]

    drcs_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for item in solution:
        drcs_count[item["RU_DRC"]] += 1

    print("[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]")
    print(drcs_count)