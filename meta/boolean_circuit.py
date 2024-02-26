import circuitgraph as cg


class Gate:
    def __init__(self, name, operation, inputs):
        self.name = name
        self.operation = operation
        self.inputs = inputs

    def eval(self, values, circuit):
        if self.operation is None:  # Input variable
            return values.get(self.name, False)
        elif self.operation in ["AND", "OR", "EQUIV", "IMPLY", "NOT", "NAND", "NOR"]:
            input_values = [
                gate.eval(values, circuit)
                if isinstance(gate, Gate)
                else values.get(gate, False)
                for gate in self.inputs
            ]
            if self.operation == "AND":
                return all(input_values)
            elif self.operation == "OR":
                return any(input_values)
            elif self.operation == "EQUIV":
                return all(input_values) or not any(input_values)
            elif self.operation == "IMPLY":
                return not input_values[0] or input_values[1]
            elif self.operation == "NOT":
                return not input_values[0]
            elif self.operation == "NAND":
                return not all(input_values)
            elif self.operation == "NOR":
                return not any(input_values)
        else:
            raise ValueError(f"Unsupported operation: {self.operation}")

    def __str__(self):
        if self.operation is None:  # Input variable
            return f"VAR({self.name})"
        return f"{self.operation}({', '.join(str(gate) for gate in self.inputs)})"


class Circuit:
    def __init__(self):
        self.graph = cg.Circuit()

    def add_input(self, input_name):
        self.graph.add(input_name, "input")

    def add_gate(self, gate_name, operation, inputs):
        self.graph.add(gate_name, operation, fanin=inputs)

    def add_output_gate(self, output_gate_name, input):
        self.graph.add(output_gate_name, "buf", output=True, fanin=[input])

    def eval(self, values):
        return {
            gate_name: self.graph.value(gate_name, values)
            for gate_name in self.graph.nodes()
        }

    def __str__(self):
        return ", ".join(self.graph.outputs())
