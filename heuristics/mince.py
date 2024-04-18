from itertools import chain, combinations

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
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


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
        if set(edge).intersection(set(C)):
            subproblem_1.add_hyperedge(edge)

    for node in set(hypergraph.nodes()).difference(set(C)):
        subproblem_2.add_node(node)
    for edge in hypergraph.hyperedges():
        if set(edge).intersection(set(hypergraph.nodes()).difference(set(C))):
            subproblem_2.add_hyperedge(edge)

    # Recursive calls to MINCE algorithm on subproblems
    subproblem_ordering_1 = mince(subproblem_1)
    subproblem_ordering_2 = mince(subproblem_2)

    return subproblem_ordering_1 + subproblem_ordering_2


def calculate(hypergraph):
    result = mince(hypergraph)
    print(result)
    result_string = " < ".join(map(lambda x: str(x), result))
    result_list = result

    return result_string, result_list
