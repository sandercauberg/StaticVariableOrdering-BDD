import os
import parser
import tempfile

import circuitgraph as cg

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

    def traverse(node, path):
        if node == bdd.true:
            assignment = [(var.var, value) for var, value in path.items()]
            minimal_assignments.append(assignment)
        elif node != bdd.false:
            var = bdd.var(node.var)
            path[var] = True
            traverse(node.high, path)
            path[var] = False
            traverse(node.low, path)
            del path[var]

    traverse(conjunction, {})

    dnf_clauses = []
    for assignment in minimal_assignments:
        print("Minimal Satisfying Assignment:", dict(assignment), assignment)
        clause = And(
            *[
                Variable(item) if value else Not(Variable(item))
                for item, value in assignment
            ]
        )
        dnf_clauses.append(clause)

    dnf_formula = Or(*dnf_clauses)

    return dnf_formula
