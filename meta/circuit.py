import circuitgraph as cg


class CustomCircuit(cg.Circuit):
    def get_ordered_inputs(self):
        """Get inputs in the order they are defined in the file."""
        nodes = self.graph.nodes
        input_nodes = [node for node, data in nodes.items() if node in self.inputs()]
        return input_nodes

    def get_ordered_outputs(self):
        """Get outputs in the order they are defined in the file."""
        nodes = self.graph.nodes
        output_nodes = [node for node, data in nodes.items() if node in self.outputs()]
        return output_nodes

    def get_gates(self):
        """Get gates in the order they are defined in the file."""
        nodes = self.graph.nodes
        gates = [node for node, data in nodes.items() if node not in self.inputs()]
        return gates

    def get_ordered_fanin(self, node):
        nodes = self.graph.nodes
        fanins = [fanin for fanin, data in nodes.items() if fanin in self.fanin(node)]
        return fanins
