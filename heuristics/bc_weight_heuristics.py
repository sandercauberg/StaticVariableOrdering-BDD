from meta.circuit import CustomCircuit


def calculate(circuit):
    circuit.inputs = CustomCircuit.get_ordered_inputs(circuit)
    circuit.output_gates = CustomCircuit.get_ordered_outputs(circuit)
    input_weights = {input_var: 0 for input_var in circuit.inputs}

    # Iterate through the input gates in the circuit
    for node in circuit.inputs:
        input_weights[node] = len(circuit.transitive_fanout(node))

    # print("Final input weights:", input_weights)

    # Sort the input variables by weights primarily and input order secondarily
    sorted_inputs = sorted(
        circuit.inputs, key=lambda x: (-input_weights[x], circuit.inputs.index(x))
    )

    # Create a result string based on the sorted input variables
    result_string = " < ".join(map(str, sorted_inputs))

    return result_string, sorted_inputs
