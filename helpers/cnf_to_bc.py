from meta.circuit import CustomCircuit
from meta.formula import Not


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


def create_boolean_circuit(cnf_formula):
    circuit = CustomCircuit()
    literals = cnf_formula.extract_variables()
    [circuit.add(f"var_{var}", node_type="input") for var in literals]
    covered_clauses = set()

    iteration_count = 0
    while literals:
        literals = extract_literal(cnf_formula, literals)
        literal = literals.pop(0)
        in_set = set()

        for clause in get_negation_clauses(cnf_formula, literal, covered_clauses):
            if len(clause) < 2:
                in_set.add(f"var_{clause[0]}")
            else:
                gate_variable = f"or_gate_{literal}_{iteration_count}"
                yi = tuple(f"var_{var}" for var in clause)
                circuit.add(gate_variable, "or", fanin=list(yi))
                in_set.add(gate_variable)

        circuit.add(f"and_gate_{literal}", "and", fanin=list(in_set))
        iteration_count += 1

    covered = []
    uncovered = []
    for clause in cnf_formula.children:
        tup = tuple(child for child in clause.children)
        if tup in covered_clauses:
            covered.append(clause)
        else:
            if len(tup) > 1:
                yi = tuple(f"var_{var}" for var in clause)
                circuit.add(str(clause), "or", fanin=list(yi))
                uncovered.append(circuit.graph.nodes.get(str(clause)))
            else:
                uncovered.append(f"var_{tup[0]}")

    gates = CustomCircuit.get_gates(circuit)
    circuit.add("output", "and", fanin=list(gates + uncovered), output=True)

    return circuit


def get_negation_clauses(cnf_formula, literal, covered_clauses):
    clauses = set()

    for clause in cnf_formula.children:
        if Not(literal) in clause.children:
            covered_clauses.add(tuple(clause.children))
            clause_children_except_not = tuple(
                child for child in clause.children if child != Not(literal)
            )
            clauses.add(clause_children_except_not)

    return clauses
