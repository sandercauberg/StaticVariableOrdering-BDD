import os
import parser
import tempfile

import circuitgraph as cg


def bc2cnf(circuit):
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
