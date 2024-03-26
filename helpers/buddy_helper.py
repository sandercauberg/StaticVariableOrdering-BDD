import re

from dd.cudd import BDD


def replace_var(match):
    var_name = match.group(1)
    return f"var_{var_name}"


def transform_graph(input_string):
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
                negated_input_formulas = [
                    f"!({input_formula})" for input_formula in input_formulas
                ]
                return f"({'&'.join(negated_input_formulas)})"
            if node_data["type"] == "and":
                return f"({'&'.join(input_formulas)})"
            if node_data["type"] == "or":
                return f"({'|'.join(input_formulas)})"
            if node_data["type"] == "nor":
                return f"!({' | '.join(f'{formula}' for formula in input_formulas)})"
            if node_data["type"] == "not":
                return f"({''.join(input_formulas)})"
            if node_data["type"] == "xor":
                return f"({' ^ '.join(input_formulas)})"
            if node_data["type"] == "buf":
                return input_formulas[0]
            # Add similar conditions for other gate types if needed
    return ""


def count_satisfying_assignments(bdd, roots):
    conjunction = bdd.true
    for root in roots:
        conjunction = bdd.apply("and", conjunction, root)
    # for assignment in bdd.pick_iter(conjunction):
    #     print("Satisfying Assignment:", assignment)
    return bdd.count(conjunction)


def create_bdd(input_format, formula, var_order, dump=False):
    # Create BDD with BuDDy
    formulas = []
    if input_format in ["bc", "v"]:
        var_names = [f"var_{var}" for var in formula.inputs]
        outputs = [
            get_logic_formula(formula, output_gate)
            for output_gate in formula.output_gates
        ]
        formulas = [transform_graph(output) for output in outputs]
    else:
        variables = formula.extract_variables()
        var_names = [f"var_{var}" for var in variables]
        formula = (
            str(formula)
            .replace("∨", r" \/ ")
            .replace("∧", r" /\ ")
            .replace("¬", "!")[1:-1]
        )
        for var in variables:
            formula = re.sub(r"\b" + re.escape(str(var)) + r"\b", f"var_{var}", formula)
        formulas.append(formula)

    bdd = BDD()
    bdd.declare(*var_names)
    roots = []

    for formula in formulas:
        root = bdd.add_expr(formula)
        roots.append(root)

    # Print BDD before reordering
    print("BDD Before Reordering:")
    print(bdd)
    print(
        "Number of satisfying assignments: "
        + str(count_satisfying_assignments(bdd, roots))
    )

    # Set the variable order
    var_names = [f"var_{var}" for var in var_order]

    new_bdd = BDD()
    new_bdd.declare(*var_names)
    new_bdd_roots = []

    for formula in formulas:
        root = new_bdd.add_expr(formula)
        new_bdd_roots.append(root)

    # Print BDD after reordering
    print("BDD After Reordering:")
    print(new_bdd)
    print(
        "Number of satisfying assignments: "
        + str(count_satisfying_assignments(new_bdd, new_bdd_roots))
    )
    assert count_satisfying_assignments(bdd, roots) == count_satisfying_assignments(
        new_bdd, new_bdd_roots
    )
    if dump:
        bdd.dump("bdd.png", roots=roots, filetype="png")
        new_bdd.dump("bdd_output.png", roots=new_bdd_roots, filetype="png")
