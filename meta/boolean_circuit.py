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
        self.gates = {}
        self.inputs = []
        self.output_gates = []

    def __str__(self):
        return ", ".join(str(output_gate) for output_gate in self.output_gates)

    def add_input(self, input_name):
        self.inputs.append(input_name)

    def add_gate(self, gate_name, operation, inputs):
        if gate_name in self.gates:
            raise ValueError(f"Gate '{gate_name}' is defined more than once.")

        # Convert input names to Gate objects if they exist
        input_gates = [
            self.gates[input_name]
            if input_name in self.gates
            else Gate(input_name, None, [])
            for input_name in inputs
        ]

        gate = Gate(gate_name, operation, input_gates)
        self.gates[gate.name] = gate

    def add_output_gate(self, output_gate_name, input):
        if input not in self.gates:
            raise ValueError(f"Output gate '{output_gate_name}' is not defined.")
        output_gate = self.gates[input]
        self.output_gates.append(output_gate)

    def eval(self, values):
        return {
            gate_name: gate.eval(values, self) for gate_name, gate in self.gates.items()
        }
