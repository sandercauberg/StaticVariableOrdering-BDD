class Gate:
    def __init__(self, name, operation, inputs):
        self.name = name
        self.operation = operation
        self.inputs = inputs

    def eval(self, values, circuit):
        if self.operation is None:  # Input variable
            return values.get(self.name, False)
        elif self.operation in ["AND", "OR", "EQUIV", "IMPLY", "NOT"]:
            print(self.inputs)
            input_values = [circuit.gates[i].eval(values, circuit) for i in self.inputs]
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
        else:
            raise ValueError(f"Unsupported operation: {self.operation}")

    def __str__(self):
        if self.operation is None:  # Input variable
            return f"VAR({self.name})"
        return f"{self.operation}({', '.join(str(gate) for gate in self.inputs)})"


class Circuit:
    def __init__(self):
        self.gates = {}
        self.inputs = set()
        self.output_gate = None

    def add_input(self, input_name):
        self.inputs.add(input_name)

    def add_gate(self, gate_name, operation, inputs):
        if gate_name in self.gates:
            raise ValueError(f"Gate '{gate_name}' is defined more than once.")
        gate = Gate(gate_name, operation, inputs)
        self.gates[gate.name] = gate

    def add_output_gate(self, output_gate_name, input):
        if input not in self.gates:
            raise ValueError(f"Output gate '{output_gate_name}' is not defined.")
        self.output_gate = self.gates[input]

    def eval(self, values):
        return {gate_name: gate.eval(values, self) for gate_name, gate in self.gates.items()}

    def __str__(self):
        return "\n".join(str(gate) for gate in self.gates.values())
