import math

from heuristics import mince
from meta.hypergraph import Hypergraph


def new_hypergraph():
    # Create a new instance of the Hypergraph class from lecture slides
    hypergraph = Hypergraph()

    # Add nodes representing variables
    variables = ["x0", "x1", "x2", "x3", "x4", "x5", "x6"]
    hypergraph.add_nodes(variables)

    hyperedges = [
        (("x0", "x4"), "e1"),
        (("x0", "x2", "x4", "x6"), "e2"),
        (("x1", "x6"), "e3"),
        (("x2", "x3", "x6"), "e4"),
        (("x4", "x5"), "e5"),
    ]

    hypergraph.add_hyperedges(hyperedges)

    return hypergraph


def test_powerset():
    hg = new_hypergraph()

    powerset = mince.powerset(hg.nodes())
    print(powerset)
    assert len(list((powerset))) == math.pow(2, len(hg.nodes()))


def test_balanced_mincut():
    hg = new_hypergraph()

    set_1_1 = set(mince.balanced_mincut(hg))
    set_1_2 = set(hg.nodes()).difference(set_1_1)

    assert set_1_1 == {"x1", "x2", "x3", "x6"}
    assert set_1_2 == {"x0", "x4", "x5"}

    hypergraph_1 = hg.copy()
    hypergraph_2 = hg.copy()
    [hypergraph_1.del_node(node) for node in set_1_2]
    [hypergraph_2.del_node(node) for node in set_1_1]

    set_2_1 = set(mince.balanced_mincut(hypergraph_1))
    set_2_2 = set(hypergraph_1.nodes()).difference(set_2_1)
    set_2_3 = set(mince.balanced_mincut(hypergraph_2))
    set_2_4 = set(hypergraph_2.nodes()).difference(set_2_3)

    assert set_2_1 == {"x2", "x3"}
    assert set_2_2 == {"x1", "x6"}
    assert set_2_3 == {"x5"}
    assert set_2_4 == {"x0", "x4"}


def test_mince():
    hg = new_hypergraph()
    result_string, result_order = mince.calculate(hg)

    assert result_order == ["x3", "x2", "x1", "x6", "x5", "x0", "x4"]
