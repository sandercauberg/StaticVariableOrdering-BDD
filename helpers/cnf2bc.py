from meta.circuit import CustomCircuit
from meta.formula import Not, And, Or, Variable


def extract_literals_on_occurrences(formula, literals):
    dependencies_list = [
        (
            variable,
            sum(variable in child.extract_variables() for child in formula.children),
        )
        for variable in literals
    ]

    sorted_dependencies = sorted(dependencies_list, key=lambda x: x[1], reverse=True)
    result = [item[0] for item in sorted_dependencies]

    return result


def extract_literals_on_dependencies(formula, literals):
    dependencies_list = []

    for variable in literals:
        visited_variables = set()
        dependencies = 0
        visited_variables.add(variable)

        for child in formula.ordered_children:
            child_variables = child.extract_variables()
            if variable in child_variables:
                dependencies += len(child_variables - visited_variables)
                visited_variables.update(child_variables)

        dependencies_list.append((variable, dependencies))

    sorted_dependencies = sorted(dependencies_list, key=lambda x: x[1], reverse=True)
    result = [item[0] for item in sorted_dependencies]

    return result


def combine_results(
    positive_result=None, negative_result=None, unprocessed_result=None
):
    # Filter out None values
    filtered_results = filter(
        lambda result: result is not None,
        [positive_result, negative_result, unprocessed_result],
    )

    # Build the combined result using the symbolic logic functions
    combined_result = And(*filtered_results) if filtered_results else None

    return combined_result


def factor_out(formula, literals):
    positive_factors = []
    negative_factors = []
    unprocessed_clauses = []
    if not literals:
        return formula
    literal = literals.pop(0)

    for clause in formula.ordered_children:
        if (
            literal in clause.children
            and len(clause.children) > 1
            and len(literals) >= 1
        ):
            positive_factors.append(
                Or(*(term for term in clause.ordered_children if term != literal))
            )
        elif (
            Not(literal) in clause.children
            and len(clause.children) > 1
            and len(literals) >= 1
        ):
            negative_factors.append(
                Or(*(term for term in clause.ordered_children if term != Not(literal)))
            )
        else:
            unprocessed_clauses.append(clause)

    if not positive_factors:
        positive_result = None
    elif len(positive_factors) < 2:
        positive_result = Or(literal, positive_factors[0])
    else:
        positive_result = Or(
            literal,
            factor_out(
                And(*positive_factors),
                extract_literals_on_occurrences(And(*positive_factors), literals),
            ),
        )
    if not negative_factors:
        negative_result = None
    elif len(negative_factors) < 2:
        negative_result = Or(Not(literal), negative_factors[0])
    else:
        negative_result = Or(
            Not(literal),
            factor_out(
                And(*negative_factors),
                extract_literals_on_occurrences(And(*negative_factors), literals),
            ),
        )

    if not unprocessed_clauses:
        unprocessed_result = None
    elif len(unprocessed_clauses) < 2:
        unprocessed_result = Or(unprocessed_clauses[0])
    else:
        unprocessed_result = factor_out(
            And(*unprocessed_clauses),
            extract_literals_on_occurrences(And(*negative_factors), literals),
        )

    final_formula = combine_results(
        positive_result, negative_result, unprocessed_result
    )

    return final_formula


def cnf2bc(cnf_formula, factor_out_method=None):
    literals = cnf_formula.extract_variables()
    if factor_out_method == "dependencies":
        sorted_literals = extract_literals_on_dependencies(cnf_formula, literals)
    else:
        sorted_literals = extract_literals_on_occurrences(cnf_formula, literals)

    formula = factor_out(cnf_formula, sorted_literals)
    circuit = CustomCircuit()
    [circuit.add(f"var_{var}", node_type="input") for var in literals]

    for var in formula.extract_negated_variables():
        circuit.add(f"not_var_{var}", "not", fanin=f"var_{var}")
    bc = to_bc(formula, circuit)
    return bc


def to_bc(formula, circuit):
    def build_circuit(formula):
        if isinstance(formula, Variable):
            return f"var_{formula}"
        elif isinstance(formula, Not):
            negated_variable = formula.child
            return f"not_var_{negated_variable}"
        elif isinstance(formula, Or):
            if len(formula.children) < 2:
                return build_circuit(next(iter(formula.children)))
            gate_name = f"or_{id(formula)}"
            fanins = [build_circuit(child) for child in formula.ordered_children]
            circuit.add(gate_name, "or", fanins)
            return gate_name
        elif isinstance(formula, And):
            if len(formula.children) < 2:
                return build_circuit(next(iter(formula.children)))
            gate_name = f"and_{id(formula)}"
            fanins = [build_circuit(child) for child in formula.ordered_children]
            circuit.add(gate_name, "and", fanins)
            return gate_name

    build_circuit(formula)
    nodes = circuit.graph.nodes
    successors = circuit.graph._succ

    gates = [node for node in nodes if node not in successors or not successors[node]]
    for gate in gates:
        get_node = circuit.graph.nodes.get(gate)
        get_node["output"] = True
    return circuit
