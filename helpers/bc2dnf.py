from helpers.cudd_helper import build_bdd_from_circuit
from meta.circuit import CustomCircuit
from meta.formula import And, Not, Or, Variable


def bc2dnf(circuit):
    var_order = CustomCircuit.get_ordered_inputs(circuit)
    bdd, roots = build_bdd_from_circuit(circuit, var_order)

    dnf_formulas = []

    def traverse(node, path):
        if node == bdd.true:
            # Create a clause for the DNF from the current path
            clause = [
                Variable(var) if value else Not(Variable(var))
                for var, value in path.items()
            ]
            return [And(*clause)]
        elif node == bdd.false:
            return []
        else:
            var_name = node.var

            # Traverse high branch (variable is True)
            path[var_name] = True
            high_clauses = traverse(bdd.let({var_name: True}, node), path.copy())

            # Traverse low branch (variable is False)
            path[var_name] = False
            low_clauses = traverse(bdd.let({var_name: False}, node), path.copy())

            # Combine clauses from both branches
            return high_clauses + low_clauses

    print("Starting DNF conversion for roots")
    print(f"Number of roots: {len(roots)}")

    for i, root in enumerate(roots):
        print(f"Processing root {i+1}/{len(roots)}")
        root_clauses = traverse(root,{})
        # print(root_clauses)
        dnf_formula = Or(*root_clauses)  # Create DNF formula for the current root
        dnf_formulas.append(dnf_formula)
    print(dnf_formulas)

    print("DNF conversion completed")
    return circuit, dnf_formulas
