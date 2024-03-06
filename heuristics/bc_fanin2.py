def initialize_visited(circuit):
    """Initialize 'visited' property for each node in the circuit."""
    for node in circuit.graph.nodes:
        circuit.graph.nodes[node]["visited"] = False

    circuit.inputs = circuit.inputs()
    circuit.output_gates = circuit.outputs()

    if not circuit.output_gates:
        raise ValueError("Output gates are not defined.")


def mark_visited(circuit, node):
    """Mark a node as visited."""
    circuit.graph.nodes.get(node)["visited"] = True


def is_visited(circuit, node):
    """Check if a node has been visited."""
    return circuit.graph.nodes.get(node)["visited"]


def bc_fanin2(circuit, node=None, order=None):
    # Initially, the output node should be the place to start from
    # TODO imaginary node for multi-output circuits
    if order is None:
        order = []
    if node is None:
        initialize_visited(circuit)
        node = next(iter(circuit.outputs()))
    mark_visited(circuit, node)

    if node in circuit.inputs:
        # Only add the node to order if it's an input node
        if node not in order:
            order.append(node)
    else:
        predecessors = circuit.graph._pred[node]
        # Sort predecessors by their fanin depths in descending order
        sorted_predecessors = sorted(
            predecessors, key=lambda x: circuit.fanin_depth(x), reverse=True
        )

        for w in sorted_predecessors:
            if not is_visited(circuit, w):
                bc_fanin2(circuit, w, order)

    result_string = " < ".join(map(str, order))

    return result_string, order
