from itertools import chain, combinations

import mtkahypar

from helpers.cnf2hypergraph import cnf2hypergraph
from meta.formula import Formula
from meta.hypergraph import Hypergraph


def calculate_hyperedge_cut(hypergraph, cut):
    # Calculate the size of the hyperedge cut for the given cut
    cut_size = 0
    for edge in hypergraph.hyperedges():
        if set(edge).intersection(cut) and not set(edge).issubset(cut):
            cut_size += 1
    return cut_size


def is_balanced_cut(hypergraph, cut):
    # Check if the given cut is a balanced cut
    num_vertices = len(hypergraph.nodes())
    return (1 / 3) * num_vertices <= len(cut) <= (2 / 3) * num_vertices


def powerset(iterable):
    """
    Generate the powerset of an iterable.
    Only include subsets with length > 1/3 and <= 1/2 of the original set.
    """
    s = list(iterable)
    return chain.from_iterable(
        combinations(s, r) for r in range(len(s) // 3, len(s) // 2 + 2)
    )


def balanced_mincut(hypergraph):
    mincut = None
    mincut_size = float("inf")

    for node in hypergraph.nodes():
        for cut in powerset(hypergraph.nodes()):
            if node in cut:
                continue  # Skip cuts that contain the node itself
            cut_size = calculate_hyperedge_cut(hypergraph, cut)
            if is_balanced_cut(hypergraph, cut) and cut_size < mincut_size:
                mincut = cut
                mincut_size = cut_size

    return mincut


def mince(hypergraph):
    if len(hypergraph.nodes()) == 1:  # If the hypergraph is fully vertex-ordered
        return [hypergraph.nodes()[0]]

    C = balanced_mincut(hypergraph)  # Calculate balanced mincut

    # Create subproblems based on balanced mincut
    subproblem_1 = Hypergraph()
    subproblem_2 = Hypergraph()

    for node in C:
        subproblem_1.add_node(node)
    for edge in hypergraph.hyperedges():
        if set(edge).issubset(set(C)):
            subproblem_1.add_hyperedge(edge)

    not_C = [node for node in hypergraph.nodes() if node not in C]
    for node in not_C:
        subproblem_2.add_node(node)
    for edge in hypergraph.hyperedges():
        if set(edge).issubset(not_C):
            subproblem_2.add_hyperedge(edge)

    # Recursive calls to MINCE algorithm on subproblems
    subproblem_ordering_1 = mince(subproblem_1)
    subproblem_ordering_2 = mince(subproblem_2)

    return subproblem_ordering_1 + subproblem_ordering_2


def kahypar(hypergraph, nodes_mapping):
    if len(hypergraph.nodes()) == 1:  # If the hypergraph is fully vertex-ordered
        return [hypergraph.nodes()[0]]

    new_hypergraph, hyperedges = hypergraph.to_kahypar()
    context = mtkahypar.Context()
    context.loadPreset(mtkahypar.PresetType.DETERMINISTIC)
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

    subproblem_ordering_1 = kahypar(hypergraph1, nodes_mapping)
    hypergraph1_mapping_reversed = {v: k for k, v in hypergraph1_mapping.items()}
    subproblem_ordering_1 = [
        nodes_mapping[hypergraph1_mapping_reversed[node]]
        for node in subproblem_ordering_1
    ]
    subproblem_ordering_2 = kahypar(hypergraph2, nodes_mapping)
    hypergraph2_mapping_reversed = {v: k for k, v in hypergraph2_mapping.items()}
    subproblem_ordering_2 = [
        nodes_mapping[hypergraph2_mapping_reversed[node]]
        for node in subproblem_ordering_2
    ]

    return subproblem_ordering_1 + subproblem_ordering_2


def calculate(formula):
    if isinstance(formula, Formula) and formula.is_cnf():
        hypergraph = cnf2hypergraph(formula)
    elif isinstance(formula, Hypergraph):
        hypergraph = formula
    else:
        raise Warning("Unknown formula input for MINCE algorithm.")
    result = mince(hypergraph)
    mapping = hypergraph.convert_nodes_to_integers()
    mapping_reversed = {v: k for k, v in mapping.items()}
    result_kahypar = kahypar(hypergraph, mapping)
    result_kahypar = [mapping_reversed[node] for node in result_kahypar]
    print(result_kahypar)
    result_string = " < ".join(map(lambda x: str(x), result))
    result_list = result

    return result_string, result_list
