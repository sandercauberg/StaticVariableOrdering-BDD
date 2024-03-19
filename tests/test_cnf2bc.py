from helpers import cnf2bc
from meta.formula import Variable


def test_extract_literals_and_dependencies():
    """Test """
    a, b, c, d, e = Variable("a"), Variable("b"), Variable("c"), Variable("d"), Variable("e")
    cnf_formula = ((a|c)&(~a|e)&(~a|~b|c)&(~a|b|~d)&(b|~d|e))
    literals = cnf_formula.extract_variables()

    assert literals == {a,b,c,d,e}  # A set is unordered

    dependencies = cnf2bc.extract_literals_and_dependencies(cnf_formula, literals)

    assert dependencies[0] == a
    assert dependencies[1] == b
    assert set(dependencies[2:]) == {c,d,e}
    assert False


