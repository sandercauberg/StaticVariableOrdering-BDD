import re

from dd import autoref


def replace_var(match):
    var_name = match.group(1)
    return f"var_{var_name}"


def transform_expression(input_string):
    # Replace VAR() with corresponding variable names
    output_string = re.sub(r"VAR\((\w+)\)", replace_var, input_string)
    output_string = re.sub(r"AND\(([^,]+),\s*([^)]+)\)", r"(\1&\2)", output_string)
    output_string = re.sub(r"OR\(([^,]+),\s*([^)]+)\)", r"(\1|\2)", output_string)

    return output_string


def transform_verilog(input_string):
    input_string = re.sub(r"VAR\((\w+)\)", replace_var, input_string)

    def replace_comma_in_nand(match):
        inner_content = match.group(2)
        inner_content = re.sub(r"nand\(([^,]+),([^)]+)\)", r"(\1|\2)", inner_content)
        return f"({match.group(1)}|{inner_content})"

    while re.search("nand", input_string):
        input_string = re.sub(
            r"nand\(([^,]+),([^)]+)\)", replace_comma_in_nand, input_string
        )

    return input_string


def get_logic_formula(circuit, gate_name, var_prefix="var_"):
    if gate_name in circuit.graph._node:
        node_data = circuit.graph._node[gate_name]
        if node_data["type"] == "input":
            return f"{var_prefix}{gate_name}"
        else:
            inputs = circuit.graph._pred[gate_name]
            input_formulas = [
                get_logic_formula(circuit, input_gate, var_prefix)
                for input_gate in inputs
            ]
            if node_data["type"] == "nand":
                return f"nand({', '.join(input_formulas)})"
            # Add similar conditions for other gate types if needed
    return ""


def create_bdd(input_format, formula, var_order):
    # Create BDD with BuDDy
    if input_format == "bc":
        var_names = [f"var_{var}" for var in formula.inputs]
        formula = transform_expression(str(formula.output_gate))
    elif input_format == "v":
        var_names = [f"var_{var}" for var in formula.inputs]
        output = get_logic_formula(formula, formula.output_gate)
        formula = transform_verilog(output)
    else:
        var_names = [f"var_{var}" for var in formula.extract_variables()]
        formula = (
            str(formula)
            .replace("∨", r" \/ ")
            .replace("∧", r" /\ ")
            .replace("¬", "!")[1:-1]
        )
        for i in range(10):
            formula = formula.replace(str(i), f"var_{i}")

    bdd = autoref.BDD()
    bdd.declare(*var_names)
    u = bdd.add_expr(formula)

    # Print BDD before reordering
    print("BDD Before Reordering:")
    print(bdd)
    print("Number of satisfying assignments: " + str(bdd.count(u)))

    # Set the variable order
    var_names = [f"var_{var}" for var in var_order]
    bdd = autoref.BDD()
    bdd.declare(*var_names)
    bdd.add_expr(formula)

    # Print BDD after reordering
    print("\nBDD After Reordering:")
    print(bdd)
