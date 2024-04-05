import pytest

from meta.formula import Variable, Not, And, Or, Formula


def test_evaluation():
    a, b, c, d = Variable("a"), Variable("b"), Variable("c"), Variable("d")
    assert (a | b).eval({a})
    assert (a & b).eval({a, b})
    assert not (a & b).eval({a})
    assert (a & b | b & c).eval({b, c})
    assert not ((a | c | ~d) & d & (b | ~c)).eval({})
    assert (~a & ~~~b).eval({})
    assert (a | ~a).eval({})
    assert ((~a | b) | (~b | a)).eval({})
    assert ((~a | a) | (~b | b)).eval({})


def test_properties():
    a, b = Variable("a"), Variable("b")
    assert Not(a) == a.__invert__()
    assert And(a, b) == a.__and__(b)
    assert Or(a, b) == a.__or__(b)
    assert a.eq(b) == b.__eq__(a)


def test_extract_variables():
    a, b, c, d = Variable("a"), Variable("b"), Variable("c"), Variable("d")
    formula = (a | c | ~d) & d & (b | ~c)
    assert formula.extract_variables() == {a, b, c, d}
    assert formula.extract_negated_variables() == {c, d}


def test_empty_formula_error():
    plain_formula = Formula()
    with pytest.raises(NotImplementedError) as e:
        plain_formula.eval({})

    assert str(e.value) == "Plain formula can not be evaluated"
