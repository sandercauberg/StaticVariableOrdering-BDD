import re
import time

from dd.cudd import BDD

from meta.circuit import CustomCircuit


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

    # Mapping of gate types to BDD operations
    gate_to_op = {
        "and": lambda *args: and_operation(args),
        "or": lambda *args: or_operation(args),
        "nand": lambda *args: bdd.apply("not", and_operation(args)),
        "nor": lambda *args: bdd.apply("not", or_operation(args)),
    }

    def and_operation(args):
        if len(args) >= 2:
            bdd_node = bdd.apply(
                "and",
                and_operation(args[: len(args) // 2]),
                and_operation(args[len(args) // 2 :]),
            )
        else:
            bdd_node = args[0]
        return bdd_node

    def or_operation(args):
        if len(args) >= 2:
            bdd_node = bdd.apply(
                "or",
                or_operation(args[: len(args) // 2]),
                or_operation(args[len(args) // 2 :]),
            )
        else:
            bdd_node = args[0]
        return bdd_node

    # Process input nodes first
    # [bdd.add_var(node) for node in var_order]

    # Traverse the Boolean circuit level by level
    max_depth = max(circuit.fanout_depth(node) for node in circuit.inputs())
    for level in range(max_depth + 1):
        for node in CustomCircuit.get_gates(circuit):
            if circuit.fanin_depth(node) == level and node not in circuit.inputs():
                node_instance = circuit.graph.nodes.get(node)
                fanin_nodes = []

                for name in CustomCircuit.get_ordered_fanin(circuit, node):
                    if name in circuit.inputs():
                        fanin_nodes.append(bdd.var(name))
                    else:
                        bdd_node = gate_nodes[name]
                        fanin_nodes.append(bdd_node)

                if node_instance["type"] == "buf":
                    roots.append(fanin_nodes[0])
                    continue
                elif node not in gate_nodes:
                    remaining_args = fanin_nodes
                    bdd_node = None

                    while remaining_args:
                        if len(remaining_args) > 2:
                            args_to_apply = remaining_args[:2]
                            remaining_args = remaining_args[2:]
                        else:
                            args_to_apply = remaining_args
                            remaining_args = []

                        op = node_instance["type"]
                        Function_u = args_to_apply[0]
                        Function_v = (
                            args_to_apply[1] if len(args_to_apply) >= 2 else None
                        )

                        bdd_op = gate_to_op.get(op)

                        if bdd_node is None:
                            if callable(bdd_op):
                                bdd_node = bdd_op(*(args_to_apply + remaining_args))
                                remaining_args = []
                            else:
                                bdd_node = bdd.apply(op, Function_u, Function_v)
                        else:
                            bdd_node = bdd.apply(op, bdd_node, Function_u)
                            if Function_v:
                                bdd_node = bdd.apply(op, bdd_node, Function_v)

                    if node_instance["output"] is True:
                        roots.append(bdd_node)
                    gate_nodes[node] = bdd_node
                else:
                    bdd_node = gate_nodes[node]

                gate_nodes[node] = bdd_node

    return bdd, roots


def create_bdd(input_format, formula, var_order, bdd={}, dump=False):
    # Create BDD with CuDD
    formulas = []
    bdd_creation_time_start = time.perf_counter()
    if input_format in ["bc", "v"] and bdd is None:
        original_order = CustomCircuit.get_ordered_inputs(formula)
        var_names = [f"var_{var}" for var in original_order]
        bdd, roots = build_bdd_from_circuit(formula, original_order)
    elif bdd is not None:
        bdd, roots = bdd.get("tree"), bdd.get("roots")
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
        bdd.configure(reordering=False)
        bdd.declare(*var_names)
        roots = []

        for formula in formulas:
            root = bdd.add_expr(formula)
            roots.append(root)

    bdd_creation_time = time.perf_counter() - bdd_creation_time_start
    bdd_satisfying_assignments = count_satisfying_assignments(bdd, roots)

    # Print BDD before reordering
    print("BDD Before Reordering:")
    print(bdd)
    print("Amount of nodes: ", len(bdd))
    print("Number of satisfying assignments: " + str(bdd_satisfying_assignments))

    new_bdd_creation_time_start = time.perf_counter()

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

    new_bdd_creation_time = time.perf_counter() - new_bdd_creation_time_start
    new_bdd_satisfying_assignments = count_satisfying_assignments(
        new_bdd, new_bdd_roots
    )

    # Print BDD after reordering
    print("BDD After Reordering:")
    print(new_bdd)
    print("Amount of nodes: ", len(new_bdd))
    print("Number of satisfying assignments: " + str(new_bdd_satisfying_assignments))
    assert bdd_satisfying_assignments == new_bdd_satisfying_assignments
    if input_format in ["bc", "v"]:
        # We cannot do this assertion as the BDD is optimized,
        # whereas the BC is not. So it may yield different results
        pass
        # assert count_satisfying_assignments(bdd, roots) ==
        # circuitgraph.sat.model_count(
        #     formula, assumptions={output: True for output in formula.outputs()}
        # )

    if dump:
        bdd.dump("bdd.png", roots=roots, filetype="png")
        new_bdd.dump("bdd_output.png", roots=new_bdd_roots, filetype="png")

    return {
        "BDD": {"tree": bdd, "roots": roots},
        "Original BDD creation time": bdd_creation_time,
        "Original BDD size": len(bdd),
        "Original BDD # of satisfying assignments": bdd_satisfying_assignments,
        "Reordered BDD creation time": new_bdd_creation_time,
        "Reordered BDD size": len(new_bdd),
        "Reordered BDD # of satisfying assignments": new_bdd_satisfying_assignments,
    }
