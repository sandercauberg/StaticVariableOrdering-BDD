def bc_fanin(circuit):
    # TODO def is_output(self, node) or circuit.outputs()
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
    output_gate = circuit.output_gates[0]

    if not circuit.output_gates:
        raise ValueError("Output gates are not defined.")

    if len(circuit.output_gates) > 1:
        circuit.add("imaginary_output", "and", fanin=circuit.output_gates, output=True)
        output_gate = "imaginary_output"

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

    calculate_depth(output_gate)

    # Sort the input variables based on both depth and original order
    sorted_inputs = sorted(
        circuit.inputs,
        key=lambda x: (
            -input_depth.get(x, 0),
            list(circuit.inputs).index(x),
            -input_depth.get(x, 0),
        ),
    )

    circuit.remove("imaginary_output")

    result_string = " < ".join(map(str, sorted_inputs))

    return result_string, sorted_inputs
