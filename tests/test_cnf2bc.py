from helpers import cnf2bc
from meta.formula import Variable, And, Or


def create_variables(*names):
    return [Variable(name) for name in names]


def create_cnf_formula(clauses):
    if not clauses:
        return None
    cnf_clauses = [Or(*[var for var in clause]) for clause in clauses]
    cnf_formula = And(*cnf_clauses)
    return cnf_formula


def test_extract_literals_and_occurrences():
    """Test"""
    a, b, c, d, e = create_variables("a", "b", "c", "d", "e")
    clauses = [(a, c), (~a, e), (~a, ~b, c), (~a, b, ~d), (b, ~d, e)]
    cnf_formula = create_cnf_formula(clauses)
    literals = cnf_formula.extract_variables()

    assert literals == {a, b, c, d, e}  # A set is unordered

    dependencies = cnf2bc.extract_literals_on_occurrences(cnf_formula, literals)

    assert dependencies[0] == a  # 4 occurrences
    assert dependencies[1] == b  # 3 occurrences
    assert set(dependencies[2:]) == {c, d, e}  # 2 occurrences


def test_extract_literals_and_dependencies():
    """Test"""
    a, b, c, d, e = create_variables("a", "b", "c", "d", "e")
    clauses = [(a, c), (~a, e), (~a, ~b, c), (~a, b, ~d), (b, ~d, e)]
    cnf_formula = create_cnf_formula(clauses)
    literals = cnf_formula.extract_variables()

    assert literals == {a, b, c, d, e}  # A set is unordered

    dependencies = cnf2bc.extract_literals_on_dependencies(cnf_formula, literals)

    assert set(dependencies[:2]) == {a, b}  # 4 dependencies
    assert set(dependencies[2:4]) == {d, e}  # 3 dependencies
    assert dependencies[4] == c  # 2 dependencies
