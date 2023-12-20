from meta.formula import Variable


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
