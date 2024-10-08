from meta.circuit import CustomCircuit


def initialize_visited(circuit):
    """Initialize 'visited' property for each node in the circuit."""
    for node in circuit.graph.nodes:
        circuit.graph.nodes[node]["visited"] = False

    circuit.output_gates = CustomCircuit.get_ordered_outputs(circuit)

    circuit.output_gate = next(iter(circuit.output_gates))

    if not circuit.output_gates:
        raise ValueError("Output gates are not defined.")

    if len(circuit.output_gates) > 1:
        circuit.add("imaginary_output", "and", fanin=circuit.output_gates, output=True)
        circuit.output_gate = "imaginary_output"


def mark_visited(circuit, node):
    """Mark a node as visited."""
    circuit.graph.nodes.get(node)["visited"] = True


def is_visited(circuit, node):
    """Check if a node has been visited."""
    return circuit.graph.nodes.get(node)["visited"]


def calculate_order(circuit, node=None, order=None):
    # Initially, the output node should be the place to start from
    if order is None:
        order = []
    if node is None:
        initialize_visited(circuit)
        node = circuit.output_gate
    inputs = CustomCircuit.get_ordered_inputs(circuit)
    mark_visited(circuit, node)

    if node in inputs:
        # Only add the node to order if it's an input node
        if node not in order:
            order.append(node)
    else:
        predecessors = circuit.graph._pred[node]
        # Sort predecessors by fanin depth primarily and input order secondarily
        sorted_predecessors = sorted(
            predecessors,
            key=lambda x: (
                circuit.fanin_depth(x),
                -inputs.index(x) if x in inputs else float("inf"),
            ),
            reverse=True,
        )

        for w in sorted_predecessors:
            if not is_visited(circuit, w):
                calculate_order(circuit, w, order)

        return order


def calculate(circuit):
    order = calculate_order(circuit)

    inputs = CustomCircuit.get_ordered_inputs(circuit)
    for input_node in inputs:
        if input_node not in order:
            order.append(input_node)

    circuit.remove("imaginary_output")

    result_string = " < ".join(map(str, order))

    return result_string, order
