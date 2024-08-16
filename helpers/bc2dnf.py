from helpers.cudd_helper import build_bdd_from_circuit
from heuristics import bc_weight_heuristics


def bc2dnf(circuit):
    string, var_order = bc_weight_heuristics.calculate(circuit)
    bdd, roots = build_bdd_from_circuit(circuit, var_order)

    dnf_formulas = []
    for i, root in enumerate(roots):
        root_clauses = bdd.pick_iter(root, care_vars=[])
        dnf_formulas.append(root_clauses)

    return circuit, dnf_formulas
