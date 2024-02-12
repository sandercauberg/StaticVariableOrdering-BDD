def bc_fanin(circuit):
    if circuit.output_gate is None:
        raise ValueError("Output gate is not defined.")

    input_depth = {input_name: 0 for input_name in circuit.inputs}

    def calculate_depth(node, current_depth=1):
        if node.operation is None:  # Input variable
            if node.name in circuit.inputs:
                input_depth[node.name] = max(input_depth[node.name], current_depth)
        else:
            for input_gate in node.inputs:
                next_depth = (
                    current_depth + 1
                    if input_gate.name not in circuit.inputs
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
