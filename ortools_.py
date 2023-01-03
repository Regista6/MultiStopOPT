from geopy.distance import geodesic
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import streamlit as st


def create_model(lat_long):
    data = {}
    data['distance_matrix'] = []
    sz = len(lat_long)+1
    data['distance_matrix'].append([0]*(sz))
    for i in range(sz-1):
        pos_i = lat_long[i]
        temp = [0]
        for j in range(sz-1):
            pos_j = lat_long[j]
            dist = geodesic(pos_i, pos_j).kilometers
            dist *= 10000000
            temp.append(int(dist))
        data['distance_matrix'].append(temp)
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(manager, routing, solution, data, lat_long, loc_identifier):
    # print('Objective: {} km'.format(solution.ObjectiveValue()/10000000))
    temp1 = ""
    temp2 = ""
    index = routing.Start(0)
    cnt = 0
    coord = []
    while not routing.IsEnd(index):
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        node = manager.IndexToNode(index)
        if node == 0:
            continue
        latitude, longitude = lat_long[node-1]
        coord.append((latitude, longitude))
        loc_identity = loc_identifier[node-1]
        cnt += 1
        temp1 += '/' + '%27' + str(latitude) + '%2C' + str(longitude) + '%27'
        temp2 += '/' + '%27' + loc_identity + '%27'
    try:
        assert (cnt == len(lat_long))
    except:
        st.write("Some locations were dropped to get a feasible solution.🤯")
        st.write(
            "One possible reason could be constraints contradicting each other.⚠️")
        st.write("For other unclear cases, increasing the time_limit could work.⌛")
    output1 = "https://www.google.com/maps/dir" + temp1
    output2 = "https://www.google.com/maps/dir" + temp2 + '/' + loc_identifier[-1]
    return output1, output2, coord


def optimize(lat_long, loc_identifier, start_idx, end_idx, priority_locs, p_d, time_lim):
    """Optimize the order of stops based on geodesic distance."""
    data = create_model(lat_long)
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    total_nodes = len(lat_long)

    routing.AddConstantDimension(
        1,  # increment by 1
        total_nodes+1,  # capacity of dim
        True,  # set count to zero
        "count_dim")
    cnt_dim = routing.GetDimensionOrDie("count_dim")

    if start_idx != 0 or end_idx != 0:
        penalty = 1_000_000_000_000_000_000
        for node in range(1, total_nodes):
            routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

    if start_idx != 0:
        cnt_dim.CumulVar(manager.NodeToIndex(start_idx)).SetValue(1)
    if end_idx != 0:
        cnt_dim.CumulVar(manager.NodeToIndex(end_idx)).SetValue(total_nodes)

    if priority_locs != "":
        priority_locs = priority_locs.split(",")
        for ch, ch1 in zip(priority_locs, priority_locs[1:]):
            loc, loc1 = int(ch), int(ch1)
            expr = cnt_dim.CumulVar(manager.NodeToIndex(
                loc1)) - cnt_dim.CumulVar(manager.NodeToIndex(loc))
            routing.solver().Add(expr == 1)

    if p_d != "":
        p_d = p_d.split(",")
        for i in range(0, len(p_d)-1, 2):
            pickup_idx, delivery_idx = manager.NodeToIndex(
                int(p_d[i])), manager.NodeToIndex(int(p_d[i+1]))
            routing.solver().Add(cnt_dim.CumulVar(pickup_idx) <= cnt_dim.CumulVar(delivery_idx))

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(time_lim)

    solution = routing.SolveWithParameters(search_parameters)

    status = routing.status()

    status_dict = {
        0: "ROUTING_NOT_SOLVED: Problem not solved yet.",
        1: "ROUTING_SUCCESS: Problem solved successfully.",
        2: "ROUTING_FAIL: No solution found to the problem.",
        3: "ROUTING_FAIL_TIMEOUT: Time limit reached before finding a solution.",
        4: "ROUTING_INVALID: Model, model parameters, or flags are not valid."
    }

    st.write(f"{status_dict[status]}")
    if solution:
        return print_solution(manager, routing, solution, data, lat_long, loc_identifier)
