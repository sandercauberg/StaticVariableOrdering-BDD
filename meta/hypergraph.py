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
    def __init__(self, nodes_mapping=None):
        """
        Initialize a hypergraph.
        """
        self.node_links = {}  # Pairing: Node -> Hyperedge
        self.edge_links = {}  # Pairing: Hyperedge -> Node
        self.edge_labels = {}  # Pairing: Hyperedge -> Label
        self.nodes_mapping = nodes_mapping  # Node mapping for KaHyPar graphs

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

    def neighbors(self, node):
        """
        Return all neighbors adjacent to the given node.
        """
        neighbors = set([])

        for e in self.node_links[node]:
            neighbors.update(set(self.edge_links[e]))

        return list(neighbors - {node})

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

    def add_nodes(self, nodelist):
        """
        Add given nodes to the hypergraph.
        """
        for each in nodelist:
            self.add_node(each)

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
        if hyperedge not in self.edge_links:
            self.edge_links[hyperedge] = []
            if label is not None:
                self.edge_labels[hyperedge] = label
            for node in hyperedge:
                if node in self.nodes():
                    self.link(node, hyperedge)
        else:
            raise ValueError("Edge %s already in graph" % hyperedge)

    def add_hyperedges(self, edgelist):
        """
        Add given hyperedges to the hypergraph, both with and without labels.
        """
        for item in edgelist:
            if isinstance(item, tuple) and isinstance(item[0], tuple):
                edge, label = item
                self.add_hyperedge(edge, label=label)
            else:
                edge = item
                self.add_hyperedge(edge)

    def del_hyperedge(self, hyperedge):
        """
        Delete the given hyperedge.
        """
        # If a label is associated with the hyperedge, we select said hyperedge
        hyperedge = next(
            key for key, value in self.edge_labels.items() if value == hyperedge
        )
        if hyperedge in self.hyperedges():
            for n in self.edge_links[hyperedge]:
                self.node_links[n].remove(hyperedge)

            del self.edge_links[hyperedge]

    def link(self, node, hyperedge):
        """
        Link given node and hyperedge.
        """
        if (
            isinstance(hyperedge, tuple)
            and len(hyperedge) == 1
            and isinstance(hyperedge[0], tuple)
        ):
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
        if hyperedge in self.node_links[node]:
            self.node_links[node].remove(hyperedge)
            self.edge_links[hyperedge].remove(node)
        else:
            raise ValueError("Link (%s, %s) is not in graph" % (node, hyperedge))

    def copy(self):
        """
        Create a copy of the hypergraph.
        """
        copied_hypergraph = Hypergraph()
        copied_hypergraph.node_links = {
            node: edges[:] for node, edges in self.node_links.items()
        }
        copied_hypergraph.edge_links = {
            edge: nodes[:] for edge, nodes in self.edge_links.items()
        }
        copied_hypergraph.edge_labels = self.edge_labels.copy()

        return copied_hypergraph

    def convert_nodes_to_integers(self):
        """
        Convert node names to integers and replace them in node_links and edge_links.
        Return the mapping.
        """
        if self.nodes_mapping is None:
            nodes_mapping = {node: idx for idx, node in enumerate(self.nodes())}

            # Replace node names in node_links
            new_node_links = {}
            for node, edges in self.node_links.items():
                new_node_links[nodes_mapping[node]] = [
                    tuple(nodes_mapping[n] for n in edge) for edge in edges
                ]

            # Replace node names in edge_links
            new_edge_links = {}
            for edge, nodes in self.edge_links.items():
                new_edge_links[tuple(nodes_mapping[n] for n in edge)] = [
                    nodes_mapping[node] for node in nodes
                ]

            # Update nodes_mapping and links
            self.nodes_mapping = nodes_mapping
            self.node_links = new_node_links
            self.edge_links = new_edge_links

        return self.nodes_mapping

    def to_kahypar(self):
        import mtkahypar

        """
        Convert the hypergraph into a format compatible with mtkahypar.

        Returns:
            MTKahyparHypergraph: A Hypergraph instance compatible with mtkahypar.
        """
        num_hypernodes = len(self.nodes())
        num_hyperedges = len(self.hyperedges())

        # Create a new instance of mtkahypar.Hypergraph based on the data
        mtkahypar_hypergraph = mtkahypar.Hypergraph(
            num_hypernodes=num_hypernodes,
            num_hyperedges=num_hyperedges,
            hyperedges=self.hyperedges(),
        )

        return mtkahypar_hypergraph, self.hyperedges()
