from helpers.cudd_helper import build_bdd_from_circuit
from meta.circuit import CustomCircuit
from meta.formula import And, Not, Or, Variable


def bc2dnf(circuit):
    var_order = CustomCircuit.get_ordered_inputs(circuit)
    bdd, roots = build_bdd_from_circuit(circuit, var_order)

    def traverse(node, path, memo):
        if node in memo:
            return memo[node]

        if node == bdd.true:
            # Create a clause for the DNF from the current path
            clause = [
                Variable(var) if value else Not(Variable(var))
                for var, value in path.items()
            ]
            memo[node] = [And(*clause)]
            return memo[node]
        elif node == bdd.false:
            memo[node] = []
            return []

        var_name = node.var

        # Traverse high branch (variable is True)
        path[var_name] = True
        high_node = bdd.let({var_name: True}, node)
        high_clauses = traverse(high_node, path.copy(), memo)

        # Traverse low branch (variable is False)
        path[var_name] = False
        low_node = bdd.let({var_name: False}, node)
        low_clauses = traverse(low_node, path.copy(), memo)

        memo[node] = high_clauses + low_clauses
        return memo[node]

    dnf_formulas = []
    print("Starting DNF conversion for roots")
    print(f"Number of roots: {len(roots)}")

    for i, root in enumerate(roots):
        print(f"Processing root {i+1}/{len(roots)}")
        subformula_clauses = traverse(root, {}, {})
        print(f"Number of clauses for root {i+1}: {len(subformula_clauses)}")
        dnf_formula = Or(*subformula_clauses)
        dnf_formulas.append(dnf_formula)
        print(f"Total number of DNF formulas so far: {len(dnf_formulas)}")

    print("DNF conversion completed")
    return circuit, dnf_formulas
