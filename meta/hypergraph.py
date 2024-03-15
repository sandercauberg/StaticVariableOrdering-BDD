# Copyright (c) 2008-2009 Pedro Matiello <pmatiello@gmail.com>
#                         Anand Jeyahar  <anand.jeyahar@gmail.com>
#                         Christian Muise <christian.muise@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.


class Hypergraph:
    def __init__(self):
        """
        Initialize a hypergraph.
        """
        self.node_links = {}  # Pairing: Node -> Hyperedge
        self.edge_links = {}  # Pairing: Hyperedge -> Node
        self.edge_labels = {}  # Pairing: Hyperedge -> Label

    def nodes(self):
        """
        Return node list.
        """
        return list(self.node_links.keys())

    def hyperedges(self):
        """
        Return hyperedge list.
        """
        return list(self.edge_links.keys())

    def has_hyperedge(self, hyperedge):
        """
        Return whether the requested node exists.
        """
        return hyperedge in self.edge_links

    def links(self, obj):
        """
        Return all nodes connected by the given hyperedge or all hyperedges
        connected to the given hypernode.
        """
        if obj in self.edge_links:
            return self.edge_links[obj]
        else:
            return self.node_links[obj]

    def neighbors(self, obj):
        """
        Return all neighbors adjacent to the given node.
        """
        neighbors = set([])

        for e in self.node_links[obj]:
            neighbors.update(set(self.edge_links[e]))

        return list(neighbors - {obj})

    def has_node(self, node):
        """
        Return whether the requested node exists.
        """
        return node in self.node_links

    def add_node(self, node):
        """
        Add given node to the hypergraph.
        """
        if node not in self.node_links:
            self.node_links[node] = []
        else:
            raise ValueError("Node %s already in graph" % node)

    def del_node(self, node):
        """
        Delete a given node from the hypergraph.
        """
        if self.has_node(node):
            for e in self.node_links[node]:
                self.edge_links[e].remove(node)

            self.node_links.pop(node)

    def add_hyperedge(self, hyperedge, label=None):
        """
        Add given hyperedge to the hypergraph.
        """
        if not isinstance(hyperedge, tuple):
            raise TypeError("Hyperedge must be a tuple")
        if hyperedge not in self.edge_links:
            self.edge_links[hyperedge] = []
            if label is not None:
                self.edge_labels[hyperedge] = label

    def add_hyperedges(self, edgelist):
        """
        Add given hyperedges to the hypergraph.
        """
        for edge, label in edgelist:
            self.add_hyperedge(edge, label=label if label else None)

    def del_hyperedge(self, hyperedge):
        """
        Delete the given hyperedge.
        """
        if hyperedge in self.hyperedges():
            for n in self.edge_links[hyperedge]:
                self.node_links[n].remove(hyperedge)

            del self.edge_links[hyperedge]

    def link(self, node, hyperedge):
        """
        Link given node and hyperedge.
        """
        hyperedge = hyperedge[0]

        if hyperedge not in self.node_links[node]:
            self.edge_links[hyperedge].append(node)
            self.node_links[node].append(hyperedge)
        else:
            raise ValueError("Link (%s, %s) already in graph" % (node, hyperedge))

    def unlink(self, node, hyperedge):
        """
        Unlink given node and hyperedge.
        """
        self.node_links[node].remove(hyperedge)
        self.edge_links[hyperedge].remove(node)
