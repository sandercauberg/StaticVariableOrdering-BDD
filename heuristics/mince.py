from parser import ParserWarning

import mtkahypar

from helpers.cnf2hypergraph import cnf2hypergraph
from meta.formula import Formula
from meta.hypergraph import Hypergraph


def kahypar(hypergraph, nodes_mapping, method="DETERMINISTIC"):
    if len(hypergraph.nodes()) == 1:  # If the hypergraph is fully vertex-ordered
        return [hypergraph.nodes()[0]]

    new_hypergraph, hyperedges = hypergraph.to_kahypar()
    context = mtkahypar.Context()
    preset_map = {
        "DETERMINISTIC": mtkahypar.PresetType.DETERMINISTIC,
        "DEFAULT": mtkahypar.PresetType.DEFAULT,
    }
    context.loadPreset(preset_map[method])
    # In the following, we partition a hypergraph into two blocks
    # with an allowed imbalance of 3% and optimize the connectivity metric
    context.setPartitioningParameters(
        2, 0.03, mtkahypar.Objective.KM1  # number of blocks  # imbalance parameter
    )  # objective function
    context.logging = False

    partitioned_hg = new_hypergraph.partition(context=context)
    hypergraph1_nodes = []
    hypergraph2_nodes = []
    hypergraph1_edges = []
    hypergraph2_edges = []

    for node in hypergraph.nodes():
        if partitioned_hg.blockID(node) == 0:
            hypergraph1_nodes.append(node)
        elif partitioned_hg.blockID(node) == 1:
            hypergraph2_nodes.append(node)
    for edge in hyperedges:
        edge_tuple = tuple(node for node in edge)
        if all(node in hypergraph1_nodes for node in edge):
            hypergraph1_edges.append(edge_tuple)
        elif all(node in hypergraph2_nodes for node in edge):
            hypergraph2_edges.append(edge_tuple)

    hypergraph1_mapping, hypergraph2_mapping = {}, {}
    original_mapping = {v: k for k, v in nodes_mapping.items()}
    for idx, node in enumerate(hypergraph1_nodes):
        original_node = original_mapping[node]
        hypergraph1_mapping[original_node] = idx
    for idx, node in enumerate(hypergraph2_nodes):
        original_node = original_mapping[node]
        hypergraph2_mapping[original_node] = idx
    for edge_idx, edge in enumerate(hypergraph1_edges):
        updated_edge = tuple(
            hypergraph1_mapping[original_mapping[node]]
            if node in original_mapping
            else node
            for node in edge
        )
        hypergraph1_edges[edge_idx] = updated_edge
    for edge_idx, edge in enumerate(hypergraph2_edges):
        updated_edge = tuple(
            hypergraph2_mapping[original_mapping[node]]
            if node in original_mapping
            else node
            for node in edge
        )
        hypergraph2_edges[edge_idx] = updated_edge
    hypergraph1_nodes = [
        hypergraph1_mapping[original_mapping[node]]
        if node in original_mapping
        else node
        for node in hypergraph1_nodes
    ]
    hypergraph2_nodes = [
        hypergraph2_mapping[original_mapping[node]]
        if node in original_mapping
        else node
        for node in hypergraph2_nodes
    ]

    hypergraph1 = Hypergraph(nodes_mapping=nodes_mapping)
    hypergraph1.add_nodes(hypergraph1_nodes)
    hypergraph1.add_hyperedges(hypergraph1_edges)

    hypergraph2 = Hypergraph(nodes_mapping=nodes_mapping)
    hypergraph2.add_nodes(hypergraph2_nodes)
    hypergraph2.add_hyperedges(hypergraph2_edges)

    subproblem_ordering_1 = kahypar(hypergraph1, nodes_mapping, method)
    hypergraph1_mapping_reversed = {v: k for k, v in hypergraph1_mapping.items()}
    subproblem_ordering_1 = [
        nodes_mapping[hypergraph1_mapping_reversed[node]]
        for node in subproblem_ordering_1
    ]
    subproblem_ordering_2 = kahypar(hypergraph2, nodes_mapping, method)
    hypergraph2_mapping_reversed = {v: k for k, v in hypergraph2_mapping.items()}
    subproblem_ordering_2 = [
        nodes_mapping[hypergraph2_mapping_reversed[node]]
        for node in subproblem_ordering_2
    ]

    return subproblem_ordering_1 + subproblem_ordering_2


def calculate(formula, method="DETERMINISTIC"):
    if isinstance(formula, Formula) and (formula.is_cnf() or formula.is_dnf()):
        hypergraph = cnf2hypergraph(formula)
    elif isinstance(formula, Hypergraph):
        hypergraph = formula
    else:
        raise ParserWarning("Unknown formula input for MINCE algorithm.")
    mapping = hypergraph.convert_nodes_to_integers()
    mapping_reversed = {v: k for k, v in mapping.items()}
    result_kahypar = kahypar(hypergraph, mapping, method)
    result = [mapping_reversed[node] for node in result_kahypar]

    result_string = " < ".join(map(lambda x: str(x), result))
    result_list = result

    return result_string, result_list
