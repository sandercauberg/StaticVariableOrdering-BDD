from helpers.cudd_helper import build_bdd_from_circuit
from meta.circuit import CustomCircuit
from meta.formula import And, Not, Or, Variable


def bc2dnf(circuit):
    var_order = CustomCircuit.get_ordered_inputs(circuit)
    bdd, roots = build_bdd_from_circuit(circuit, var_order)

    conjunction = bdd.false
    for root in roots:
        conjunction = bdd.apply("or", conjunction, root)

    dnf_clauses = []

    def traverse(root):
        stack = [(root, {})]

        while stack:
            node, path = stack.pop()

            if node == bdd.true:
                # Create a clause for the DNF from the current path
                clause = [
                    Variable(var) if value else Not(Variable(var))
                    for var, value in path.items()
                ]
                dnf_clauses.append(And(*clause))
            elif node != bdd.false:
                var_name = node.var

                # Traverse high branch (variable is True)
                path[var_name] = True
                high_node = bdd.let({var_name: True}, node)
                stack.append((high_node, path.copy()))

                # Traverse low branch (variable is False)
                path[var_name] = False
                low_node = bdd.let({var_name: False}, node)
                stack.append((low_node, path.copy()))

    traverse(conjunction)
    dnf_formula = Or(*dnf_clauses)

    return dnf_formula
