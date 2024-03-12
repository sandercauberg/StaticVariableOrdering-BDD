from meta.circuit import CustomCircuit
from meta.formula import Not, And, Or


def extract_literal(formula, literals):
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


def factor_out(formula, literal):
    positive_factors = []
    negative_factors = []
    unprocessed_clauses = []

    for clause in formula.children:
        if literal in clause.children:
            positive_factors.append(
                And(*(term for term in clause.children if term != literal))
            )
        elif Not(literal) in clause.children:
            negative_factors.append(
                Or(*(term for term in clause.children if term != Not(literal)))
            )
        else:
            unprocessed_clauses.append(clause)

    positive_result = Or(literal, And(*positive_factors)) if positive_factors else True
    negative_result = (
        Or(Not(literal), And(*negative_factors)) if negative_factors else True
    )

    return And(positive_result, negative_result, *unprocessed_clauses)


def cnf2bc(cnf_formula):
    circuit = CustomCircuit()
    literals = cnf_formula.extract_variables()
    [circuit.add(f"var_{var}", node_type="input") for var in literals]
    literals = extract_literal(cnf_formula, literals)
    literal = literals.pop(0)

    formula = factor_out(cnf_formula, literal)
    to_bc(formula)


def to_bc(formula):
    circuit = CustomCircuit()
    literals = formula.extract_variables()
    [circuit.add(f"var_{var}", node_type="input") for var in literals]

    for var in formula.extract_negated_variables():
        circuit.add(f"var_¬{var}", "not", fanin=f"var_{var}")

    print(formula)
    # TODO: we now have positive inputs and negations for literals, now add
    #  AND and OR gates accordingly.
