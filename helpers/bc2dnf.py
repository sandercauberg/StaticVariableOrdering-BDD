from helpers.cudd_helper import build_bdd_from_circuit
from meta.circuit import CustomCircuit
from meta.formula import And, Not, Or, Variable


def bc2dnf(circuit):
    var_order = CustomCircuit.get_ordered_inputs(circuit)
    bdd, roots = build_bdd_from_circuit(circuit, var_order)

    conjunction = bdd.false
    for root in roots:
        conjunction = bdd.apply("or", conjunction, root)

    minimal_assignments = list()

    def traverse(node, path, negated=0):
        if node == bdd.true:
            if negated % 2 == 0:
                assignment = [(var.var, value) for var, value in path.items()]
                minimal_assignments.append(assignment)
        elif node == bdd.false:
            if negated % 2 == 1:
                assignment = [(var.var, value) for var, value in path.items()]
                minimal_assignments.append(assignment)
        elif node != bdd.false:
            var = bdd.var(node.var)
            path[var] = True
            traverse(node.high, path, (negated + 1 if node.negated else negated))
            path[var] = False
            traverse(node.low, path, (negated + 1 if node.negated else negated))
            del path[var]

    traverse(conjunction, {})

    dnf_clauses = []
    for assignment in minimal_assignments:
        clause = And(
            *[
                Variable(item) if value else Not(Variable(item))
                for item, value in assignment
            ]
        )
        dnf_clauses.append(clause)

    dnf_formula = Or(*dnf_clauses)

    return dnf_formula
