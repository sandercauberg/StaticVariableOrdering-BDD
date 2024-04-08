from meta.hypergraph import Hypergraph


def cnf2hypergraph(cnf_formula):
    literals = cnf_formula.extract_variables()

    hypergraph = Hypergraph()
    hypergraph.add_nodes(literals)

    for edge_name, hyperedge in enumerate(cnf_formula.ordered_children, 1):
        if len(hyperedge.extract_variables()) < 2:
            continue
        if hypergraph.has_hyperedge(tuple(hyperedge.extract_variables())):
            continue
        hypergraph.add_hyperedge(tuple(hyperedge.extract_variables()), f"e{edge_name}")

    return hypergraph
