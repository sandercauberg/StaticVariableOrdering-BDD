from meta.hypergraph import Hypergraph


def cnf2hypergraph(cnf_formula):
    hypergraph = Hypergraph()

    if isinstance(cnf_formula, list):
        existing_edges = set()
        nodes = set()

        for gen in cnf_formula:
            # Process each generator
            for edge_dict in gen:
                # Convert the dict_keys object to a tuple for immutability
                edge_set = tuple(edge_dict.keys())

                # Add edge_set directly to the set if it's not already there
                if edge_set not in existing_edges:
                    existing_edges.add(edge_set)
                    for node in edge_set:
                        nodes.add(node)

        hypergraph.add_nodes(nodes)
        hypergraph.add_hyperedges(existing_edges)
        return hypergraph

    literals = cnf_formula.extract_variables()
    hypergraph.add_nodes(literals)

    for edge_name, hyperedge in enumerate(cnf_formula.ordered_children, 1):
        if len(hyperedge.extract_variables()) < 2:
            continue
        if hypergraph.has_hyperedge(tuple(hyperedge.extract_variables())):
            continue
        hypergraph.add_hyperedge(tuple(hyperedge.extract_variables()), f"e{edge_name}")

    return hypergraph
