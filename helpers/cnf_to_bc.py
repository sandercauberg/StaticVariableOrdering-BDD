from circuitgraph import Circuit

from meta.formula import Not


def create_boolean_circuit(cnf_formula):
    circuit = Circuit()  # G (gates in circuit)
    literals = cnf_formula.extract_variables()  # S
    [circuit.add(f"var_{var}", node_type='input') for var in literals]
    # cnf_formula Σ

    iteration_count = 0
    while literals:
        literal = literals.pop()
        in_set = set()
        print('now checking for literal ' + str(literal))

        for clause in get_negation_clauses(cnf_formula, literal):
            print(clause)
            if len(clause) < 2:
                in_set.add(f"var_{clause[0]}")
            else:
                gate_variable = f"or_gate_{literal}_{iteration_count}"
                yi = tuple(f"var_{var}" for var in clause)
                circuit.add(gate_variable, 'or', fanin=list(yi))
                in_set.add(gate_variable)

        circuit.add(f"and_gate_{literal}", 'and', fanin=list(in_set))
        iteration_count += 1

    return circuit


def get_negation_clauses(cnf_formula, literal):
    clauses = set()

    for clause in cnf_formula.children:
        if Not(literal) in clause.children:
            print(clause)
            clause_children_except_not = tuple(child for child in clause.children if child != Not(literal))
            clauses.add(clause_children_except_not)

    return clauses
