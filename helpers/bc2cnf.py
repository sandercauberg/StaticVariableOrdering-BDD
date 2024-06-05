import os
import parser
import tempfile

import circuitgraph as cg

from helpers.cudd_helper import build_bdd_from_circuit
from meta.circuit import CustomCircuit


def bc2cnf(circuit):
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

    for assignment in minimal_assignments:
        print("Minimal Satisfying Assignment:", dict(assignment))

    cnf_formula, variables = cg.sat.cnf(circuit)
    cnf_formula_str = str(cnf_formula).split("from_string='")[1].split("')")[0]
    cnf_formula_str = cnf_formula_str.replace("\\n", "\n")

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(cnf_formula_str)
        temp_file_path = temp_file.name
    try:
        input_format, formula = parser.load(temp_file_path)
    finally:
        # Clean up the temporary file
        if temp_file_path:
            os.remove(temp_file_path)

    return formula
