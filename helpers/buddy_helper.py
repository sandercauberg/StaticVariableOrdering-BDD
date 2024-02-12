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


def create_bdd(input_format, formula, var_order):
    # Create BDD with BuDDy
    if input_format == "bc":
        var_names = [f"var_{var}" for var in formula.inputs]
        formula = transform_expression(str(formula.output_gate))
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
