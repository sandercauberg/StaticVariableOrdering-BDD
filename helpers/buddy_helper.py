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


def build_bdd_from_circuit(circuit, var_order):
    bdd = BDD()
    bdd.configure(reordering=False)
    bdd.declare(*var_order)
    gate_nodes = {}
    roots = []

    # Process input nodes first
    for node in var_order:
        bdd.add_var(node)

    # Traverse the Boolean circuit level by level
    max_depth = max(circuit.fanout_depth(node) for node in circuit.inputs)
    for level in range(max_depth + 1):
        print("Processing level:", level)
        for node in circuit.graph.nodes:
            if circuit.fanin_depth(node) == level:
                print("Processing node:", node)
                if node in circuit.inputs:
                    print("Node is an input.")
                    continue
                else:
                    print("Node is a gate.")
                    node_instance = circuit.graph.nodes.get(node)
                    print("Node instance:", node_instance)
                    fanin_nodes = []
                    for name in circuit.fanin(node):
                        if name in circuit.inputs:
                            print("Fanin node is an input:", name)
                            fanin_nodes.append(bdd.var(name))
                        else:
                            print("Fanin node is a gate node:", name)
                            if name not in gate_nodes:
                                print("Creating new BDD node for gate:", name)
                                bdd_node = bdd.add_var(name)
                                gate_nodes[name] = bdd_node
                            else:
                                print("Reusing existing BDD node for gate:", name)
                                bdd_node = gate_nodes[name]
                            fanin_nodes.append(bdd_node)
                    print("Fanin nodes:", fanin_nodes)
                    if node_instance["type"] == "buf":
                        print("buf node", node, node_instance)
                        roots.append(fanin_nodes[0])
                        continue
                    elif node not in gate_nodes:
                        print("Creating new BDD node for gate:", node)
                        if node_instance["output"] is True:
                            print("OUTPUT")
                            # TODO add the output function to the roots list
                        bdd_node = bdd.apply(node_instance["type"], *fanin_nodes)
                        gate_nodes[node] = bdd_node
                    else:
                        print("Reusing existing BDD node for gate:", node)
                        bdd_node = gate_nodes[node]

                    gate_nodes[node] = bdd_node
                    print("BDD node for gate:", node, "is", bdd_node)

    return bdd, roots


def create_bdd(input_format, formula, var_order, dump=False):
    # Create BDD with CuDD
    formulas = []
    if input_format in ["bc", "v"]:
        original_order = formula.get_ordered_inputs()
        var_names = [f"var_{var}" for var in original_order]
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

    if input_format in ["bc", "v"]:
        print("original", original_order, "var order", var_order)
        bdd, roots = build_bdd_from_circuit(formula, original_order)
    else:
        bdd = BDD()
        bdd.configure(reordering=False)
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
    # var_names = [f"var_{var}" for var in var_order]
    print("order:", var_order)

    if input_format in ["bc", "v"]:
        new_bdd, new_bdd_roots = build_bdd_from_circuit(formula, var_order)
    else:
        new_bdd = BDD()
        new_bdd.configure(reordering=False)
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
