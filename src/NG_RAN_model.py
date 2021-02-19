import time
import json
from docplex.mp.model import Model
from docplex.util.environment import get_environment


class Path:
    def __init__(self, id, source, target, seq, p1, p2, p3, delay_p1, delay_p2, delay_p3):
        self.id = id
        self.source = source
        self.target = target
        self.seq = seq
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.delay_p1 = delay_p1
        self.delay_p2 = delay_p2
        self.delay_p3 = delay_p3

    def __str__(self):
        return "ID: {}\tSEQ: {}\t P1: {}\t P2: {}\t P3: {}\t dP1: {}\t dP2: {}\t dP3: {}".format(self.id, self.seq, self.p1, self.p2, self.p3, self.delay_p1, self.delay_p2, self.delay_p3)


#incluir RAM na chamada
class CR:
    def __init__(self, id, cpu, num_BS):
        self.id = id
        self.cpu = cpu
        self.num_BS = num_BS
        #self.ram = ram

    def __str__(self):
        return "ID: {}\tCPU: {}".format(self.id, self.cpu)


class DRC:
    def __init__(self, id, cpu_CU, cpu_DU, cpu_RU, ram_CU, ram_DU, ram_RU, Fs_CU, Fs_DU, Fs_RU, delay_BH, delay_MH,
                 delay_FH, bw_BH, bw_MH, bw_FH):
        self.id = id

        self.cpu_CU = cpu_CU
        self.ram_CU = ram_CU
        self.Fs_CU = Fs_CU

        self.cpu_DU = cpu_DU
        self.ram_DU = ram_DU
        self.Fs_DU = Fs_DU

        self.cpu_RU = cpu_RU
        self.ram_RU = ram_RU
        self.Fs_RU = Fs_RU

        self.delay_BH = delay_BH
        self.delay_MH = delay_MH
        self.delay_FH = delay_FH

        self.bw_BH = bw_BH
        self.bw_MH = bw_MH
        self.bw_FH = bw_FH


class FS:
    def __init__(self, id, f_cpu, f_ram):
        self.id = id
        self.f_cpu = f_cpu
        self.f_ram = f_ram


class RU:
    def __init__(self, id, CR):
        self.id = id
        self.CR = CR

    def __str__(self):
        return "RU: {}\tCR: {}".format(self.id, self.CR)


# Global vars
links = []
capacity = {}
delay = {}
crs = {}
paths = {}
conj_Fs = {}


def read_topology_T1():
    """
    READ T1 TOPOLOGY FILE
    Implements the topology from reading the json file and creates the main structure that is used by the stages of the model.
    :rtype: Inserts topology data into global structures, so the method has no return
    """
    with open('topo_files/test_file_links.json') as json_file:
        data = json.load(json_file)

        # Creates the set of links with delay and capacity read by the json file, stores the links in the global list "links"
        json_links = data["links"]
        for item in json_links:
            link = json_links[item]
            source = link["source"]
            destination = link["destination"]

            split = str(source["node"]).rsplit('N', 1)
            if source["node"] != "CN":
                source_node = int(split[1])
            else:
                source_node = 0

            split = str(destination["node"]).rsplit('N', 1)
            if destination["node"] != "CN":
                destination_node = int(split[1])
            else:
                destination_node = 0

            # Creates links full duplex for each link in the json file
            capacity[(source_node, destination_node)] = int(str(link["linkCapacity"]))
            delay[(source_node, destination_node)] = float(str(link["LinkDelay"]).replace(',', '.'))
            if (source_node, destination_node) != '':
                links.append((source_node, destination_node))

            # creates links full duplex for each link in the json file
            capacity[(destination_node, source_node)] = int(str(link["linkCapacity"]))
            delay[(destination_node, source_node)] = float(str(link["LinkDelay"]).replace(',', '.'))
            if (destination_node, source_node) != '':
                links.append((destination_node, source_node))

        # Creates the set of CRs with RAM and CPU in a global list "crs" -- crs[0] is the network Core node
        with open('RU_0_1_high.json') as json_file:
            data = json.load(json_file)
            json_nodes = data["nodes"]
            for item in json_nodes:
                split = str(item).rsplit('-', 1)
                CR_id = split[1]
                node = json_nodes[item]
                #node_RAM = node["RAM"]
                node_CPU = node["CPU"]
                cr = CR(int(CR_id), node_CPU, 0)
                crs[int(CR_id)] = cr
        crs[0] = CR(0, 0, 0)

        # Creates the set of previously calculated paths "paths.json". -- the algorithm used to calculate the paths is the k-shortest paths algorithm.
        with open('paths.json') as json_paths_file:
            # Reads the file "paths.json" with the paths
            json_paths_f = json.load(json_paths_file)
            json_paths = json_paths_f["paths"]

            # For each path it calculates the id, sets the origin (Core node) and destination (CRs with RUs).
            for item in json_paths:
                path = json_paths[item]
                path_id = path["id"]
                path_source = path["source"]

                if path_source == "CN":
                    path_source = 0

                path_target = path["target"]
                path_seq = path["seq"]

                # sets the paths p1, p2 and p3 (BH, MH and FH respectively)
                paths_p = [path["p1"], path["p2"], path["p3"]]

                list_p1 = []
                list_p2 = []
                list_p3 = []

                for path_p in paths_p:
                    aux = ""
                    sum_delay = 0

                    for tup in path_p:
                        aux += tup
                        tup_aux = tup
                        tup_aux = tup_aux.replace('(', '')
                        tup_aux = tup_aux.replace(')', '')
                        tup_aux = tuple(map(int, tup_aux.split(', ')))
                        if path_p == path["p1"]:
                            list_p1.append(tup_aux)
                        elif path_p == path["p2"]:
                            list_p2.append(tup_aux)
                        elif path_p == path["p3"]:
                            list_p3.append(tup_aux)
                        sum_delay += float(str(delay[tup_aux]).replace(',', '.'))

                    if path_p == path["p1"]:
                        delay_p1 = sum_delay
                    elif path_p == path["p2"]:
                        delay_p2 = sum_delay
                    elif path_p == path["p3"]:
                        delay_p3 = sum_delay

                    if path_seq[0] == 0:
                        delay_p1 = 0

                    if path_seq[1] == 0:
                        delay_p2 = 0

                # Creates the paths and store at the global dict "paths"
                p = Path(path_id, path_source, path_target, path_seq, list_p1, list_p2, list_p3, delay_p1, delay_p2, delay_p3)
                paths[path_id] = p


def read_topology_T2():
    """
    READ T1 TOPOLOGY FILE
    Implements the topology from reading the json file and creates the main structure that is used by the stages of the model.
    :rtype: Inserts topology data into global structures, so the method has no return
    """
    with open('topo_files/test_file_links.json') as json_file:
        data = json.load(json_file)

        # Creates the set of links with delay and capacity read by the json file, stores the links in the global list "links"
        json_links = data["links"]
        for item in json_links:
            link = item
            source_node = link["fromNode"]
            destination_node = link["toNode"]

            # Creates links full duplex for each link in the json file
            if source_node < destination_node:
                capacity[(source_node, destination_node)] = link["capacity"]
                delay[(source_node, destination_node)] = link["delay"]
                links.append((source_node, destination_node))

            # Creates links full duplex for each link in the json file
            else:
                capacity[(destination_node, source_node)] = link["capacity"]
                delay[(destination_node, source_node)] = link["delay"]
                links.append((destination_node, source_node))

        # Creates the set of CRs with RAM and CPU in a global list "crs" -- cr[0] is the network Core node
        with open('topo_files/test_file_nodes.json') as json_file:
            data = json.load(json_file)
            json_nodes = data["nodes"]
            for item in json_nodes:
                node = item
                CR_id = node["nodeNumber"]
                #node_RAM = node["RAM"]
                node_CPU = node["cpu"]
                cr = CR(CR_id, node_CPU, 0)
                crs[CR_id] = cr
        crs[0] = CR(0, 0, 0)

        # Creates the set of previously calculated paths "paths.json". -- the algorithm used to calculate the paths is the k-shortest paths algorithm.
        with open('paths.json') as json_paths_file:
            # Reads the file "paths.json" with the paths
            json_paths_f = json.load(json_paths_file)
            json_paths = json_paths_f["paths"]

            # For each path it calculates the id, sets the origin (Core node) and destination (CRs with RUs).
            for item in json_paths:
                path = json_paths[item]
                path_id = path["id"]
                path_source = path["source"]

                if path_source == "CN":
                    path_source = 0

                path_target = path["target"]
                path_seq = path["seq"]

                # sets the paths p1, p2 and p3 (BH, MH and FH respectively)
                paths_p = [path["p1"], path["p2"], path["p3"]]

                list_p1 = []
                list_p2 = []
                list_p3 = []

                for path_p in paths_p:
                    aux = ""
                    sum_delay = 0

                    for tup in path_p:
                        aux += tup
                        tup_aux = tup
                        tup_aux = tup_aux.replace('(', '')
                        tup_aux = tup_aux.replace(')', '')
                        tup_aux = tuple(map(int, tup_aux.split(', ')))
                        if path_p == path["p1"]:
                            list_p1.append(tup_aux)
                        elif path_p == path["p2"]:
                            list_p2.append(tup_aux)
                        elif path_p == path["p3"]:
                            list_p3.append(tup_aux)
                        sum_delay += delay[tup_aux]

                    if path_p == path["p1"]:
                        delay_p1 = sum_delay
                    elif path_p == path["p2"]:
                        delay_p2 = sum_delay
                    elif path_p == path["p3"]:
                        delay_p3 = sum_delay

                    if path_seq[0] == 0:
                        delay_p1 = 0

                    if path_seq[1] == 0:
                        delay_p2 = 0

                # Creates the paths and store at the global dict "paths"
                p = Path(path_id, path_source, path_target, path_seq, list_p1, list_p2, list_p3, delay_p1, delay_p2, delay_p3)
                paths[path_id] = p


def DRC_structure_T1():
    """
    IMPLEMENTS T1 Topology DRCs
    Implements the DRCs defined with cpu usage, ram usage, VNFs splits and network resources requirements, for T1 Topology
    :rtype: Dict with the DRCs informations
    """
    # Creates the DRCs
    # DRCs MAP (id: DRC): 1 = DRC1, 2 = DRC2, 4 = DRC7 and 5 = DRC8 -- DRCs with 3 independents CRs [CU]-[DU]-[RU]
    DRC1 = DRC(1, 0.49, 2.058, 2.352, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 3, 5.4, 17.4)
    DRC2 = DRC(2, 0.98, 1.568, 2.352, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 3, 5.4, 17.4)
    DRC4 = DRC(4, 0.49, 1.225, 3.185, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 3, 5.4, 5.6)
    DRC5 = DRC(5, 0.98, 0.735, 3.185, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 3, 5.4, 5.6)

    # DRCs MAP (id: DRC): 6 = DRC12, 7 = DRC13, 9 = DRC18 and 10 = DRC17  -- DRCs with 2 CRs [CU/DU]-[RU] or [CU]-[DU/RU]
    DRC6 = DRC(6, 0, 0.49, 4.41, 0, 0.01, 0.01, [0], ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 3, 5.4)
    DRC7 = DRC(7, 0, 3, 3.92, 0, 0.01, 0.01, [0], ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 3, 5.4)
    DRC9 = DRC(9, 0, 2.54, 2.354, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 0, 10, 0.25, 0, 3, 17.4)
    DRC10 = DRC(10, 0, 1.71, 3.185, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 0, 10, 0.25, 0, 3, 5.6)

    # DRCs MAP (id: DRC): 8 = DRC19 -- D-RAN with 1 CR [CU/DU/RU]
    DRC8 = DRC(8, 0, 0, 4.9, 0, 0, 0.01, [0], [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 0, 10, 0, 0, 3)

    # Creates the set of DRCs
    DRCs = {1: DRC1, 2: DRC2, 4: DRC4, 5: DRC5, 6: DRC6, 7: DRC7, 8: DRC8, 9: DRC9, 10: DRC10}

    return DRCs


def DRC_structure_T2():
    """
        IMPLEMENTS T2 Topology DRCs
        Implements the DRCs defined with cpu usage, ram usage, VNFs splits and network resources requirements, for T2 Topology
        :rtype: Dict with the DRCs informations
        """
    # Creates the DRCs
    # DRCs MAP (id: DRC): 1 = DRC1, 2 = DRC2, 4 = DRC7 and 5 = DRC8 -- DRCs with 3 independents CRs [CU]-[DU]-[RU]
    DRC1 = DRC(1, 0.49, 2.058, 2.352, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 42.6)
    DRC2 = DRC(2, 0.98, 1.568, 2.352, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 42.6)
    DRC4 = DRC(4, 0.49, 1.225, 3.185, 0.01, 0.01, 0.01, ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 13.6)
    DRC5 = DRC(5, 0.98, 0.735, 3.185, 0.01, 0.01, 0.01, ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 10, 10, 0.25, 9.9, 13.2, 13.6)

    # DRCs MAP (id: DRC): 6 = DRC12, 7 = DRC13, 9 = DRC18 and 10 = DRC17  -- DRCs with 2 CRs [CU/DU]-[RU] or [CU]-[DU/RU]
    DRC6 = DRC(6, 0, 0.49, 4.41, 0, 0.01, 0.01, [0], ['f8'], ['f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 9.9, 13.2)
    DRC7 = DRC(7, 0, 3, 3.92, 0, 0.01, 0.01, [0], ['f8', 'f7'], ['f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 10, 10, 0, 9.9, 13.2)
    DRC9 = DRC(9, 0, 2.54, 2.354, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2'], ['f1', 'f0'], 0, 10, 0.25, 0, 9.9, 42.6)
    DRC10 = DRC(10, 0, 1.71, 3.185, 0, 0.01, 0.01, [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3'], ['f2', 'f1', 'f0'], 0, 10, 0.25, 0, 3, 13.6)

    # DRCs MAP (id: DRC): 8 = DRC19 -- D-RAN with 1 CR [CU/DU/RU]
    DRC8 = DRC(8, 0, 0, 4.9, 0, 0, 0.01, [0], [0], ['f8', 'f7', 'f6', 'f5', 'f4', 'f3', 'f2', 'f1', 'f0'], 0, 0, 10, 0, 0, 9.9)

    # Creates the set of DRCs
    DRCs = {1: DRC1, 2: DRC2, 4: DRC4, 5: DRC5, 6: DRC6, 7: DRC7, 8: DRC8, 9: DRC9, 10: DRC10}

    return DRCs


def RU_location_T1():
    """
    SET THE T1 TOPOLOGY RUs
    Reads the T1 Topology file and define the RUs locations
    :return: Dict with RUs information
    """
    rus = {}
    count = 1
    #Reads the topology file with RUs locations
    with open('RU_0_1_high.json') as json_file:
        data = json.load(json_file)
        json_crs = data["nodes"]
        for item in json_crs:
            node = json_crs[item]
            num_rus = node["RU"]
            num_cr = str(item).split('-', 1)[1]

            # Creates the RUs
            for i in range(0, num_rus):
                rus[count] = RU(count, int(num_cr))
                count += 1

    return rus


def RU_location_T2():
    """
    SET THE T2 TOPOLOGY RUs
    Reads the T2 Topology file and define the RUs locations
    :return: Dict with RUs information
    """

    rus = {}
    count = 1
    # Reads the topology file with RUs locations
    with open('topo_files/test_file_nodes.json') as json_file:
        data = json.load(json_file)

        json_crs = data["nodes"]

        for item in json_crs:
            node = item
            num_rus = node["RU"]
            num_cr = node["nodeNumber"]

            # Creates the RUs
            for i in range(0, num_rus):
                rus[count] = RU(count, int(num_cr))
                count += 1

    return rus


#global vars that manages the warm_start for stage 2 and stage 3
DRC_f1 = 0
f1_vars = []
f2_vars = []


def run_stage_1():
    """
    RUN THE STAGE 1
    This method uses the topology main structure to calculate the optimal solution of the Stage 1
    :rtype: (int) This method returns the Objective Function value of the Stage 1
    """

    print("Running Stage - 1")
    print("-----------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()

    # read_topology_T1()
    read_topology_T2()

    # DRCs = DRC_structure_T1()
    DRCs = DRC_structure_T2()

    # rus = RU_location_T1()
    rus = RU_location_T2()

    # Creates the set of Fs (functional splits)
    # Fs(id, f_cpu, f_ram)
    F1 = FS('f8', 2, 2)
    F2 = FS('f7', 2, 2)
    F3 = FS('f6', 2, 2)
    F4 = FS('f5', 2, 2)
    F5 = FS('f4', 2, 2)
    F6 = FS('f3', 2, 2)
    F7 = FS('f2', 2, 2)
    F8 = FS('f1', 2, 2)
    F9 = FS('f0', 2, 2)
    conj_Fs = {'f8': F1, 'f7': F2, 'f6': F3, 'f5': F4, 'f4': F5, 'f3': F6, 'f2': F7}

    # Creates the Stage 1 model
    mdl = Model(name='NGRAN Problem', log_output=True)
    # Set the GAP value (the model execution stop when GAP hits the value -- Default: 0%)
    mdl.parameters.mip.tolerances.mipgap = 0.10

    # Tuple used by the decision variable management
    i = [(p, d, b) for p in paths for d in DRCs for b in rus if paths[p].seq[2] == rus[b].CR]

    # Creates the decision variable x
    mdl.x = mdl.binary_var_dict(i, name='x')

    # Stage 1 - Objective Function
    mdl.minimize(mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if c in paths[it[0]].seq)) for c in crs if crs[c].id != 0) - mdl.sum(
        mdl.sum(mdl.max(0, (mdl.sum(mdl.x[it] for it in i if ((o in DRCs[it[1]].Fs_CU and paths[it[0]].seq[0] == crs[c].id) or (
                    o in DRCs[it[1]].Fs_DU and paths[it[0]].seq[1] == crs[c].id) or (
                                                                          o in DRCs[it[1]].Fs_RU and paths[it[0]].seq[
                                                                      2] == crs[c].id))) - 1)) for o in conj_Fs) for c in crs))
    # Constraint 1 - Unicity
    for b in rus:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[2] == b) == 1, 'unicity')

    # Constrains 1.1 - kill paths with wrong destination
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].target != rus[it[2]].CR) == 0, 'path')

    # Constraint 1.2 - only paths with 2 CRs can pick NG-RAN(2) splits -- [CU/DU]-[RU] or [CU]-[DU/RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] != 0 and (it[1] == 6 or it[1] == 7 or it[1] == 8 or it[1] == 9 or it[1] == 10)) == 0, 'DRCs_path_pick')

    # Constraint 1.3 - only paths with 3 CRs can pick NG-RAN(3) splits - [CU]-[DU]-[RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and it[1] != 6 and it[1] != 7 and it[1] != 8 and it[1] != 9 and it[1] != 10) == 0, 'DRCs_path_pick2')

    # Constraint 1.4 - only paths with 1 CR can pick D-RAN split - [CU/DU/RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] == 0 and it[1] != 8) == 0, 'DRCs_path_pick3')

    # constraint 1.5 - paths with 2 CRs do not pick D-RAN splits
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] != 0 and it[1] == 8) == 0, 'DRCs_path_pick4')

    # #constraint 1.6 - the destination node of the path p must be the CR with the RU b
    for ru in rus:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[2] != rus[ru].CR and it[2] == rus[ru].id) == 0)

    # Constraint 2 - Link capacity constraint
    for l in links:
        for k in links:
            if l[0] == k[1] and l[1] == k[0]:
                break
        mdl.add_constraint(mdl.sum(mdl.x[it] * DRCs[it[1]].bw_BH for it in i if l in paths[it[0]].p1) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_MH for it in i if l in paths[it[0]].p2) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_FH for it in i if l in paths[it[0]].p3) +
                           mdl.sum(mdl.x[it] * DRCs[it[1]].bw_BH for it in i if k in paths[it[0]].p1) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_MH for it in i if k in paths[it[0]].p2) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_FH for it in i if k in paths[it[0]].p3)
                           <= capacity[l], 'links_bw')

    # Constraint 3 - Link delay constraint for BH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p1) <= DRCs[it[1]].delay_BH, 'delay_req_p1')

    # Constraint 4 - Link delay constraint for MH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p2) <= DRCs[it[1]].delay_MH, 'delay_req_p2')

    # Constraint 5 - Link delay constraint for FH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p3 <= DRCs[it[1]].delay_FH), 'delay_req_p3')

    # Constraint 6 - CPU usage constraint
    for c in crs:
        mdl.add_constraint(mdl.sum(mdl.x[it] * DRCs[it[1]].cpu_CU for it in i if c == paths[it[0]].seq[0]) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].cpu_DU for it in i if c == paths[it[0]].seq[1]) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].cpu_RU for it in i if c == paths[it[0]].seq[2]) <= crs[c].cpu, 'crs_cpu_usage')

    # Constraint 7 - RAM usage constraint
    # for c in crs:
    #     mdl.add_constraint(mdl.sum(mdl.x[it] * DRCs[it[1]].ram_CU for it in i if c == paths[it[0]].seq[0]) + mdl.sum(
    #         mdl.x[it] * DRCs[it[1]].ram_DU for it in i if c == paths[it[0]].seq[1]) + mdl.sum(
    #         mdl.x[it] * DRCs[it[1]].ram_RU for it in i if c == paths[it[0]].seq[2]) <= crs[c].ram, 'crs_ram_usage')

    alocation_time_end = time.time()
    start_time = time.time()
    mdl.solve()
    end_time = time.time()
    print("Stage 1 - Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    print("Stage 1 - Enlapsed Time: {}".format(end_time - start_time))
    for it in i:
        if mdl.x[it].solution_value > 0:
            print("x{} -> {}".format(it, mdl.x[it].solution_value))
            print(paths[it[0]].seq)

    disp_Fs = {}

    for cr in crs:
        disp_Fs[cr] = {'f8': 0, 'f7': 0, 'f6': 0, 'f5': 0, 'f4': 0, 'f3': 0, 'f2': 0, 'f1': 0, 'f0': 0}

    for it in i:
        for cr in crs:
            if mdl.x[it].solution_value == 1:
                if cr in paths[it[0]].seq:
                    seq = paths[it[0]].seq
                    if cr == seq[0]:
                        Fs = DRCs[it[1]].Fs_CU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

                    if cr == seq[1]:
                        Fs = DRCs[it[1]].Fs_DU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

                    if cr == seq[2]:
                        Fs = DRCs[it[1]].Fs_RU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

    print("FO: {}".format(mdl.solution.get_objective_value()))

    for cr in disp_Fs:
        print(str(cr) + str(disp_Fs[cr]))

    global f1_vars
    for it in i:
        if mdl.x[it].solution_value > 0:
            f1_vars.append(it)

    return mdl.solution.get_objective_value()


def run_stage_2(FO_Stage_1):
    """
    RUN THE STAGE 2
    This method uses the topology main structure to calculate the optimal solution of the Stage 2
    :rtype: (int) This method returns the Objective Function value of the Stage 2
    """

    print("Running Stage - 2")
    print("-----------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()

    # read_topology_T1()
    read_topology_T2()

    # DRCs = DRC_structure_T1()
    DRCs = DRC_structure_T2()

    # rus = RU_location_T1()
    rus = RU_location_T2()

    # Creates the set of Fs (functional splits)
    # Fs(id, f_cpu, f_ram)
    F1 = FS('f8', 2, 2)
    F2 = FS('f7', 2, 2)
    F3 = FS('f6', 2, 2)
    F4 = FS('f5', 2, 2)
    F5 = FS('f4', 2, 2)
    F6 = FS('f3', 2, 2)
    F7 = FS('f2', 2, 2)
    F8 = FS('f1', 2, 2)
    F9 = FS('f0', 2, 2)
    conj_Fs = {'f8': F1, 'f7': F2, 'f6': F3, 'f5': F4, 'f4': F5, 'f3': F6, 'f2': F7}

    # Creates the Stage 1 model
    mdl = Model(name='NGRAN Problem2', log_output=True)
    # Set the GAP value (the model execution stop when GAP hits the value -- Default: 0%)
    mdl.parameters.mip.tolerances.mipgap = 0

    # Tuple used by the decision variable management
    i = [(p, d, b) for p in paths for d in DRCs for b in rus if paths[p].seq[2] == rus[b].CR]

    # Creates the decision variable x
    mdl.x = mdl.binary_var_dict(i, name='x')

    # Stage 2 - Objective Function
    mdl.minimize(mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if it[1] == DRC)) for DRC in DRCs))

    # Constraint Stage 1
    mdl.add_constraint(mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if c in paths[it[0]].seq)) for c in crs if crs[c].id != 0) - mdl.sum(mdl.sum(mdl.max(0, (mdl.sum(mdl.x[it] for it in i if ((o in DRCs[it[1]].Fs_CU and paths[it[0]].seq[0] == crs[c].id) or (o in DRCs[it[1]].Fs_DU and paths[it[0]].seq[1] == crs[c].id) or (o in DRCs[it[1]].Fs_RU and paths[it[0]].seq[2] == crs[c].id))) - 1)) for o in conj_Fs) for c in crs) == FO_Stage_1)

    # Constraint 1 - Unicity
    for b in rus:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[2] == b) == 1, 'unicity')

    # Constrains 1.1 - kill paths with wrong destination
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].target != rus[it[2]].CR) == 0, 'path')

    # Constraint 1.2 - only paths with 2 CRs can pick NG-RAN(2) splits -- [CU/DU]-[RU] or [CU]-[DU/RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] != 0 and (
                it[1] == 6 or it[1] == 7 or it[1] == 8 or it[1] == 9 or it[1] == 10)) == 0, 'DRCs_path_pick')

    # Constraint 1.3 - only paths with 3 CRs can pick NG-RAN(3) splits - [CU]-[DU]-[RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if
                               paths[it[0]].seq[0] == 0 and it[1] != 6 and it[1] != 7 and it[1] != 8 and it[1] != 9 and
                               it[1] != 10) == 0, 'DRCs_path_pick2')
    # Constraint 1.4 - only paths with 1 CR can pick D-RAN split - [CU/DU/RU]
    mdl.add_constraint(
        mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] == 0 and it[1] != 8) == 0,
        'DRCs_path_pick3')

    # constraint 1.5 - paths with 2 CRs do not pick D-RAN splits
    mdl.add_constraint(
        mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] != 0 and it[1] == 8) == 0,
        'DRCs_path_pick4')

    # #constraint 1.6 - the destination node of the path p must be the CR with the RU b
    for ru in rus:
        mdl.add_constraint(
            mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[2] != rus[ru].CR and it[2] == rus[ru].id) == 0)

    # Constraint 2 - Link capacity constraint
    for l in links:
        for k in links:
            if l[0] == k[1] and l[1] == k[0]:
                break
        mdl.add_constraint(mdl.sum(mdl.x[it] * DRCs[it[1]].bw_BH for it in i if l in paths[it[0]].p1) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_MH for it in i if l in paths[it[0]].p2) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_FH for it in i if l in paths[it[0]].p3) +
                           mdl.sum(mdl.x[it] * DRCs[it[1]].bw_BH for it in i if k in paths[it[0]].p1) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_MH for it in i if k in paths[it[0]].p2) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_FH for it in i if k in paths[it[0]].p3)
                           <= capacity[l], 'links_bw')

    # Constraint 3 - Link delay constraint for BH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p1) <= DRCs[it[1]].delay_BH, 'delay_req_p1')

    # Constraint 4 - Link delay constraint for MH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p2) <= DRCs[it[1]].delay_MH, 'delay_req_p2')

    # Constraint 5 - Link delay constraint for FH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p3 <= DRCs[it[1]].delay_FH), 'delay_req_p3')

    # Constraint 6 - CPU usage constraint
    for c in crs:
        mdl.add_constraint(
            mdl.sum(mdl.x[it] * DRCs[it[1]].cpu_CU for it in i if c == paths[it[0]].seq[0]) + mdl.sum(
                mdl.x[it] * DRCs[it[1]].cpu_DU for it in i if c == paths[it[0]].seq[1]) + mdl.sum(
                mdl.x[it] * DRCs[it[1]].cpu_RU for it in i if c == paths[it[0]].seq[2]) <= crs[c].cpu,
            'crs_cpu_usage')

    # Constraint 7 - RAM usage constraint
    # for c in crs:
    #     mdl.add_constraint(
    #         mdl.sum(mdl.x[it] * DRCs[it[1]].ram_CU for it in i if c == paths[it[0]].seq[0]) + mdl.sum(
    #             mdl.x[it] * DRCs[it[1]].ram_DU for it in i if c == paths[it[0]].seq[1]) + mdl.sum(
    #             mdl.x[it] * DRCs[it[1]].ram_RU for it in i if c == paths[it[0]].seq[2]) <= crs[c].ram,
    #         'crs_ram_usage')

    warm_start = mdl.new_solution()
    for it in f1_vars:
        warm_start.add_var_value(mdl.x[it], 1)
    mdl.add_mip_start(warm_start)
    alocation_time_end = time.time()

    start_time = time.time()
    mdl.solve()
    end_time = time.time()

    print("Stage 2 - Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    print("Stage 2 - Enlapsed Time: {}".format(end_time - start_time))

    for it in i:
        if mdl.x[it].solution_value == 1:
            print("x{} -> {}".format(it, mdl.x[it].solution_value))
            print(paths[it[0]].seq)

    disp_Fs = {}

    for cr in crs:
        disp_Fs[cr] = {'f8': 0, 'f7': 0, 'f6': 0, 'f5': 0, 'f4': 0, 'f3': 0, 'f2': 0, 'f1': 0, 'f0': 0}

    for it in i:
        for cr in crs:
            if mdl.x[it].solution_value == 1:
                if cr in paths[it[0]].seq:
                    seq = paths[it[0]].seq
                    if cr == seq[0]:
                        Fs = DRCs[it[1]].Fs_CU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

                    if cr == seq[1]:
                        Fs = DRCs[it[1]].Fs_DU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

                    if cr == seq[2]:
                        Fs = DRCs[it[1]].Fs_RU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

    print("FO: {}".format(mdl.solution.get_objective_value()))

    for cr in disp_Fs:
        print(str(cr) + str(disp_Fs[cr]))

    global f2_vars
    for it in i:
        if mdl.x[it].solution_value > 0:
            f2_vars.append(it)

    return mdl.solution.get_objective_value()


def run_stage_3(FO_Stage_1, FO_Stage_2):
    """
    RUN THE STAGE 3
    This method uses the topology main structure to calculate the optimal solution of the Stage 3
    :rtype: (int) This method returns the Objective Function value of the Stage 3
    """

    print("Running Stage - 3")
    print("-----------------------------------------------------------------------------------------------------------")
    alocation_time_start = time.time()

    # read_topology_T1()
    read_topology_T2()

    # DRCs = DRC_structure_T1()
    DRCs = DRC_structure_T2()

    # rus = RU_location_T1()
    rus = RU_location_T2()

    # Creates the set of Fs (functional splits)
    # Fs(id, f_cpu, f_ram)
    F1 = FS('f8', 2, 2)
    F2 = FS('f7', 2, 2)
    F3 = FS('f6', 2, 2)
    F4 = FS('f5', 2, 2)
    F5 = FS('f4', 2, 2)
    F6 = FS('f3', 2, 2)
    F7 = FS('f2', 2, 2)
    F8 = FS('f1', 2, 2)
    F9 = FS('f0', 2, 2)
    conj_Fs = {'f8': F1, 'f7': F2, 'f6': F3, 'f5': F4, 'f4': F5, 'f3': F6, 'f2': F7}

    #set of DRC priority
    DRC_p = {1: 4, 2: 1, 4: 6, 5: 5, 6: 10, 7: 9, 8: 25, 9: 7, 10: 8}

    # Creates the Stage 1 model
    mdl = Model(name='NGRAN Problem3', log_output=True)
    # Set the GAP value (the model execution stop when GAP hits the value -- Default: 0%)
    mdl.parameters.mip.tolerances.mipgap = 0

    # Tuple used by the decision variable management
    i = [(p, d, b) for p in paths for d in DRCs for b in rus if paths[p].seq[2] == rus[b].CR]

    # Creates the decision variable x
    mdl.x = mdl.binary_var_dict(i, name='x')

    #Stage 3 Objective Function
    mdl.minimize(mdl.sum(mdl.sum(mdl.x[it] * DRC_p[it[1]] for it in i if it[1] == DRC) for DRC in DRCs))

    # Constraint Stage 2
    mdl.add_constraint(mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if it[1] == DRC)) for DRC in DRCs) == FO_Stage_2)

    # Constraint Stage 1
    mdl.add_constraint(mdl.sum(mdl.min(1, mdl.sum(mdl.x[it] for it in i if c in paths[it[0]].seq)) for c in crs if crs[c].id != 0) - mdl.sum(mdl.sum(mdl.max(0, (mdl.sum(mdl.x[it] for it in i if ((o in DRCs[it[1]].Fs_CU and paths[it[0]].seq[0] == crs[c].id) or (o in DRCs[it[1]].Fs_DU and paths[it[0]].seq[1] == crs[c].id) or (o in DRCs[it[1]].Fs_RU and paths[it[0]].seq[2] == crs[c].id))) - 1)) for o in conj_Fs) for c in crs) == FO_Stage_1)

    # Constraint 1 - Unicity
    for b in rus:
        mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if it[2] == b) == 1, 'unicity')

    # Constrains 1.1 - kill paths with wrong destination
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].target != rus[it[2]].CR) == 0, 'path')

    # Constraint 1.2 - only paths with 2 CRs can pick NG-RAN(2) splits -- [CU/DU]-[RU] or [CU]-[DU/RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] != 0 and (
                it[1] == 6 or it[1] == 7 or it[1] == 8 or it[1] == 9 or it[1] == 10)) == 0, 'DRCs_path_pick')

    # Constraint 1.3 - only paths with 3 CRs can pick NG-RAN(3) splits - [CU]-[DU]-[RU]
    mdl.add_constraint(mdl.sum(mdl.x[it] for it in i if
                               paths[it[0]].seq[0] == 0 and it[1] != 6 and it[1] != 7 and it[1] != 8 and it[1] != 9 and
                               it[1] != 10) == 0, 'DRCs_path_pick2')

    # Constraint 1.4 - only paths with 1 CR can pick D-RAN split - [CU/DU/RU]
    mdl.add_constraint(
        mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] == 0 and it[1] != 8) == 0,
        'DRCs_path_pick3')

    # constraint 1.5 - paths with 2 CRs do not pick D-RAN splits
    mdl.add_constraint(
        mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[0] == 0 and paths[it[0]].seq[1] != 0 and it[1] == 8) == 0,
        'DRCs_path_pick4')

    # #constraint 1.6 - the destination node of the path p must be the CR with the RU b
    for ru in rus:
        mdl.add_constraint(
            mdl.sum(mdl.x[it] for it in i if paths[it[0]].seq[2] != rus[ru].CR and it[2] == rus[ru].id) == 0)

    # Constraint 2 - Link capacity constraint
    for l in links:
        for k in links:
            if l[0] == k[1] and l[1] == k[0]:
                break
        mdl.add_constraint(mdl.sum(mdl.x[it] * DRCs[it[1]].bw_BH for it in i if l in paths[it[0]].p1) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_MH for it in i if l in paths[it[0]].p2) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_FH for it in i if l in paths[it[0]].p3) +
                           mdl.sum(mdl.x[it] * DRCs[it[1]].bw_BH for it in i if k in paths[it[0]].p1) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_MH for it in i if k in paths[it[0]].p2) + mdl.sum(
            mdl.x[it] * DRCs[it[1]].bw_FH for it in i if k in paths[it[0]].p3)
                           <= capacity[l], 'links_bw')

    # Constraint 3 - Link delay constraint for BH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p1) <= DRCs[it[1]].delay_BH, 'delay_req_p1')

    # Constraint 4 - Link delay constraint for MH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p2) <= DRCs[it[1]].delay_MH, 'delay_req_p2')

    # Constraint 5 - Link delay constraint for FH
    for it in i:
        mdl.add_constraint((mdl.x[it] * paths[it[0]].delay_p3 <= DRCs[it[1]].delay_FH), 'delay_req_p3')

    # Constraint 6 - CPU usage constraint
    for c in crs:
        mdl.add_constraint(
            mdl.sum(mdl.x[it] * DRCs[it[1]].cpu_CU for it in i if c == paths[it[0]].seq[0]) + mdl.sum(
                mdl.x[it] * DRCs[it[1]].cpu_DU for it in i if c == paths[it[0]].seq[1]) + mdl.sum(
                mdl.x[it] * DRCs[it[1]].cpu_RU for it in i if c == paths[it[0]].seq[2]) <= crs[c].cpu,
            'crs_cpu_usage')

    # Constraint 7 - RAM usage constraint
    # for c in crs:
    #     mdl.add_constraint(
    #         mdl.sum(mdl.x[it] * DRCs[it[1]].ram_CU for it in i if c == paths[it[0]].seq[0]) + mdl.sum(
    #             mdl.x[it] * DRCs[it[1]].ram_DU for it in i if c == paths[it[0]].seq[1]) + mdl.sum(
    #             mdl.x[it] * DRCs[it[1]].ram_RU for it in i if c == paths[it[0]].seq[2]) <= crs[c].ram,
    #         'crs_ram_usage')

    alocation_time_end = time.time()
    start_time = time.time()
    warm_start = mdl.new_solution()
    for it in f2_vars:
        warm_start.add_var_value(mdl.x[it], 1)

    mdl.add_mip_start(warm_start)
    mdl.solve()
    end_time = time.time()

    print("Stage 3 - Alocation Time: {}".format(alocation_time_end - alocation_time_start))
    print("Stage 3 - Enlapsed Time: {}".format(end_time - start_time))

    for it in i:
        if mdl.x[it].solution_value == 1:
            print("x{} -> {}".format(it, mdl.x[it].solution_value))
            print(paths[it[0]].seq)

    # with get_environment().get_output_stream("solution.json") as fp:
    #     mdl.solution.export(fp, "json")

    disp_Fs = {}

    for cr in crs:
        disp_Fs[cr] = {'f8': 0, 'f7': 0, 'f6': 0, 'f5': 0, 'f4': 0, 'f3': 0, 'f2': 0, 'f1': 0, 'f0': 0}

    for it in i:
        for cr in crs:
            if mdl.x[it].solution_value == 1:
                if cr in paths[it[0]].seq:
                    seq = paths[it[0]].seq
                    if cr == seq[0]:
                        Fs = DRCs[it[1]].Fs_CU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

                    if cr == seq[1]:
                        Fs = DRCs[it[1]].Fs_DU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

                    if cr == seq[2]:
                        Fs = DRCs[it[1]].Fs_RU
                        for o in Fs:
                            if o != 0:
                                dct = disp_Fs[cr]
                                dct["{}".format(o)] += 1
                                disp_Fs[cr] = dct

    print("FO: {}".format(mdl.solution.get_objective_value()))

    for cr in disp_Fs:
        print(str(cr) + str(disp_Fs[cr]))


if __name__ == '__main__':
    start_all = time.time()

    FO_Stage_1 = run_stage_1()
    FO_Stage_2 = run_stage_2(FO_Stage_1)
    run_stage_3(FO_Stage_1, FO_Stage_2)

    end_all = time.time()

    print("TOTAL TIME: {}".format(end_all - start_all))