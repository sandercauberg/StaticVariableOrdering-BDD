def bc_weight_heuristics(circuit):
    nodes_with_output_true = [
        gate for gate, data in circuit.graph.nodes.items() if data.get("output")
    ]
    nodes_with_input_true = [
        node
        for node, data in circuit.graph.nodes.items()
        if data.get("type") == "input"
    ]
    circuit.inputs = nodes_with_input_true
    circuit.output_gates = nodes_with_output_true
    input_weights = {input_var: 0 for input_var in circuit.inputs}

    def calculate_weights(node, visited=None):
        if visited is None:
            visited = set()

        get_node = circuit.graph.nodes.get(node)

        if node in visited or get_node.get("output"):
            return 0

        visited.add(node)

        fanout_nodes = circuit.fanout(node)

        if get_node.get("type") == "input":
            weight = 0
        else:
            weight = 1
        for successor in fanout_nodes:
            weight += calculate_weights(successor, visited)

        return weight

    # Iterate through the output gates in the circuit
    for gate in circuit.inputs:
        input_weights[gate] = calculate_weights(gate, set())

    print("Final input weights:", input_weights)

    # Sort the input variables based on their weights in decreasing order
    sorted_inputs = sorted(circuit.inputs, key=lambda x: -input_weights[x])

    # Create a result string based on the sorted input variables
    result_string = " < ".join(map(str, sorted_inputs))

    return result_string, sorted_inputs
