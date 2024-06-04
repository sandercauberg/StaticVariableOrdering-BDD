import gc
import time

from dd import cudd

from meta.circuit import CustomCircuit
from meta.formula import Not


def count_satisfying_assignments(bdd, roots):
    conjunction = bdd.false
    for root in roots:
        conjunction = bdd.apply("or", conjunction, root)
    # for assignment in bdd.pick_iter(conjunction):
    #     print("Satisfying Assignment:", assignment)
    return bdd.count(conjunction, nvars=len(bdd.vars))


def build_bdd_from_circuit(circuit, var_order):
    bdd = cudd.BDD(memory_estimate=1024**3)
    bdd.configure(
        reordering=False,
        garbage_collection=True,
        max_memory=1024**3,
    )
    bdd.declare(*var_order)
    gate_nodes = {}
    roots = []

    # Mapping of gate types to BDD operations
    gate_to_op = {
        "and": lambda *args: and_or_operation("and", args),
        "or": lambda *args: and_or_operation("or", args),
        "nand": lambda *args: bdd.apply("not", and_or_operation("and", args)),
        "nor": lambda *args: bdd.apply("not", and_or_operation("or", args)),
    }

    def and_or_operation(op, args):
        if len(args) >= 2:
            node = bdd.apply(
                op,
                and_or_operation(op, args[: len(args) // 2]),
                and_or_operation(op, args[len(args) // 2 :]),
            )
        else:
            node = args[0]
        return node

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


def build_bdd_from_cnf_formula(formula, var_order):
    bdd = cudd.BDD(memory_estimate=2 * 1024**3)
    bdd.configure(
        reordering=False,
        garbage_collection=True,
        max_memory=2 * 1024**3,
    )
    bdd.declare(*var_order)

    def handle_clause(clause):
        clause_node = None
        args = clause.ordered_children
        while len(args) > 0:
            if len(args) >= 2:
                Function_u = args[0]
                if isinstance(Function_u, Not):
                    Function_u = bdd.apply("not", bdd.var(Function_u.child))
                else:
                    Function_u = bdd.var(Function_u)
                Function_v = args[1]
                if isinstance(Function_v, Not):
                    Function_v = bdd.apply("not", bdd.var(Function_v.child))
                else:
                    Function_v = bdd.var(Function_v)

                if clause_node is None:
                    clause_node = bdd.apply("or", Function_u, Function_v)
                else:
                    clause_node = bdd.apply("or", clause_node, Function_u)
                    clause_node = bdd.apply("or", clause_node, Function_v)
                args = args[2:]
            elif len(args) == 1:
                Function_u = args[0]
                if isinstance(Function_u, Not):
                    Function_u = bdd.apply("not", bdd.var(Function_u.child))
                else:
                    Function_u = bdd.var(Function_u)

                if clause_node:
                    clause_node = bdd.apply("or", clause_node, Function_u)
                else:
                    clause_node = Function_u
                args = []
            else:
                args = []
        return clause_node

    first_node = handle_clause(formula.ordered_children[0])
    node = None
    for child in formula.ordered_children[1:]:
        if first_node:
            node = bdd.apply("and", first_node, handle_clause(child))
            first_node = None
        else:
            node = bdd.apply("and", node, handle_clause(child))
    roots = [node]
    return bdd, roots


def create_bdd(input_format, formula, var_order, dump=False):
    # Create BDD with CuDD
    bdd_creation_time_start = time.perf_counter()
    if input_format in ["bc", "v"]:
        bdd, roots = build_bdd_from_circuit(formula, var_order)
    else:
        bdd, roots = build_bdd_from_cnf_formula(formula, var_order)

    bdd_creation_time = time.perf_counter() - bdd_creation_time_start
    # bdd_satisfying_assignments = count_satisfying_assignments(bdd, roots)

    # Print BDD before reordering
    print("BDD Statistics:")
    print(bdd)
    print("Amount of nodes: ", len(bdd))
    print("creation time:", bdd_creation_time)
    # print("Number of satisfying assignments: " + str(bdd_satisfying_assignments))

    if dump:
        bdd.dump("bdd.png", roots=roots, filetype="png")

    gc.collect()

    return {
        "BDD creation time": bdd_creation_time,
        "BDD size": len(bdd),
    }
