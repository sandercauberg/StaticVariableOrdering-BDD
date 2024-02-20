def bc_fanin(circuit):
    nodes_with_output_true = {
        node: data for node, data in circuit.graph.nodes.items() if data.get("output")
    }
    nodes_with_input_true = {
        node: data
        for node, data in circuit.graph.nodes.items()
        if data.get("type") == "input"
    }
    circuit.inputs = nodes_with_input_true
    circuit.output_gate = next(iter(nodes_with_output_true.keys()))

    if circuit.output_gate is None:
        raise ValueError("Output gate is not defined.")

    input_depth = {input_name: 0 for input_name in circuit.inputs}

    def calculate_depth(node, current_depth=1):
        get_node = circuit.graph.nodes.get(node)
        if get_node.get("type") == "input":  # Input variable
            if node in circuit.inputs:
                input_depth[node] = max(input_depth[node], current_depth)
        else:
            for input_gate in circuit.graph._pred[node]:
                next_depth = (
                    current_depth + 1
                    if input_gate not in circuit.inputs
                    else current_depth
                )
                calculate_depth(input_gate, current_depth=next_depth)

    calculate_depth(circuit.output_gate)

    # Sort the input variables based on both depth and original order
    sorted_inputs = sorted(
        circuit.inputs,
        key=lambda x: (
            -input_depth.get(x, 0),
            list(circuit.inputs).index(x),
            -input_depth.get(x, 0),
        ),
    )

    result_string = " < ".join(map(str, sorted_inputs))

    return result_string, sorted_inputs
