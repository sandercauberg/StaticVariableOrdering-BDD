import pytest

from meta.hypergraph import Hypergraph


def new_hypergraph():
    # Create a new instance of the Hypergraph class
    hypergraph = Hypergraph()

    # Add nodes representing variables
    variables = ["x1", "x2", "x3", "x4", "x5"]
    for variable in variables:
        hypergraph.add_node(variable)

    # Define hyperedges with labels
    hyperedges = [
        (("x1", "x2", "x3"), "e1"),
        (("x1", "x4"), "e2"),
        (("x4", "x5"), "e3"),
    ]

    hypergraph.add_hyperedges(hyperedges)

    return hypergraph


def test_raise_exception_on_duplicate_node_addition():
    hg = Hypergraph()
    hg.add_node("x1")
    with pytest.raises(ValueError) as e:
        hg.add_node("x1")
    assert str(e.value) == "Node x1 already in graph"


def test_raise_exception_on_duplicate_edge_addition():
    hg = Hypergraph()
    hg.add_hyperedge("e1")
    with pytest.raises(ValueError) as e:
        hg.add_hyperedge("e1")
    assert str(e.value) == "Edge e1 already in graph"


def test_raise_exception_on_duplicate_edge_link():
    hg = Hypergraph()
    hg.add_node("x1")
    hg.add_hyperedge("e1")
    hg.link("x1", "e1")
    with pytest.raises(ValueError) as e:
        hg.link("x1", "e1")
    assert str(e.value) == "Link (x1, e1) already in graph"


def test_raise_exception_on_non_existing_link_removal():
    hg = Hypergraph()
    hg.add_node("x1")
    hg.add_hyperedge("e1")
    with pytest.raises(ValueError) as e:
        hg.unlink("x1", "e1")
    assert str(e.value) == "Link (x1, e1) is not in graph"


def test_raise_exception_when_edge_added_from_non_existing_node():
    hg = Hypergraph()
    hg.add_nodes(["x1", "x2"])
    with pytest.raises(KeyError) as e:
        hg.link("x3", "x1")
    assert str(e.value) == "'x3'"
    assert hg.neighbors("x1") == []


def test_raise_exception_when_edge_added_to_non_existing_node():
    hg = Hypergraph()
    hg.add_nodes(["x1", "x2"])
    with pytest.raises(KeyError) as e:
        hg.link("x1", "x3")
    assert str(e.value) == "'x3'"
    assert hg.neighbors("x1") == []


def test_remove_node():
    hg = new_hypergraph()
    hg.del_node("x1")

    # Check that the deleted node is indeed removed from the hypergraph
    assert "x1" not in hg.nodes()

    # Check that the non-removed nodes are still in the hypergraph
    for e in hg.hyperedges():
        for n in hg.links(e):
            assert n in hg.nodes()


def test_remove_edge():
    hg = new_hypergraph()
    assert len(hg.hyperedges()) == 3

    hg.del_hyperedge("e1")

    # Check that the deleted hyperedge is indeed removed from the hypergraph
    assert len(hg.hyperedges()) == 2

    # Check that the non-removed hyperedges are still in the hypergraph
    for e in hg.hyperedges():
        assert e in hg.hyperedges()


def test_hypergraph_link_unlink_link():
    hg = Hypergraph()
    hg.add_nodes(["x1", "x2"])
    hg.add_hyperedges(["e1"])

    hg.link("x1", "e1")
    hg.unlink("x1", "e1")
    hg.link("x1", "e1")
