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

        for child in formula.children:
            child_variables = child.extract_variables()
            if variable in child_variables:
                dependencies += len(child_variables - visited_variables)
                visited_variables.update(child_variables)

        dependencies_list.append((variable, dependencies))

    sorted_dependencies = sorted(dependencies_list, key=lambda x: x[1], reverse=True)
    result = [item[0] for item in sorted_dependencies]

    return result


def factor_out(formula, literals):
    positive_factors = []
    negative_factors = []
    unprocessed_clauses = []
    literal = literals.pop(0)

    for clause in formula.children:
        if (
            literal in clause.children
            and len(clause.children) > 1
            and len(literals) >= 1
        ):
            positive_factors.append(
                Or(*(term for term in clause.children if term != literal))
            )
        elif (
            Not(literal) in clause.children
            and len(clause.children) > 1
            and len(literals) >= 1
        ):
            negative_factors.append(
                Or(*(term for term in clause.children if term != Not(literal)))
            )
        else:
            unprocessed_clauses.append(clause)

    positive_result = (
        Or(literal, factor_out(And(*positive_factors), literals))
        if positive_factors
        else None
    )
    negative_result = (
        Or(Not(literal), factor_out(And(*negative_factors), literals))
        if negative_factors
        else None
    )

    if negative_result and positive_result:
        final_formula = And(positive_result, negative_result, *unprocessed_clauses)
    elif positive_result:
        final_formula = And(positive_result, *unprocessed_clauses)
    elif negative_result:
        final_formula = And(negative_result, *unprocessed_clauses)
    else:
        final_formula = And(*unprocessed_clauses)

    return final_formula


def cnf2bc(cnf_formula):
    circuit = CustomCircuit()
    literals = cnf_formula.extract_variables()
    [circuit.add(f"var_{var}", node_type="input") for var in literals]
    literals = extract_literals_on_occurrences(cnf_formula, literals)

    formula = factor_out(cnf_formula, literals)
    circuit = CustomCircuit()
    literals = formula.extract_variables()
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
            fanins = [build_circuit(child) for child in formula.children]
            circuit.add(gate_name, "or", fanins)
            return gate_name
        elif isinstance(formula, And):
            if len(formula.children) < 2:
                return build_circuit(next(iter(formula.children)))
            gate_name = f"and_{id(formula)}"
            fanins = [build_circuit(child) for child in formula.children]
            circuit.add(gate_name, "and", fanins)
            return gate_name

    build_circuit(formula)
    return circuit
