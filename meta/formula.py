class Formula:
    def __invert__(self):
        return Not(self)

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.eq(other)

    def eval(self, v):
        raise NotImplementedError("Plain formula can not be valuated")


class BinOp(Formula):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return (
            "("
            + " {} ".format(self.operator).join(map(str, self.children))
            + ")"
        )

    __repr__ = __str__

    def eq(self, other):
        return self.children == other.children


class And(BinOp):
    operator = "∧"

    def eval(self, v):
        return all(child.eval(v) for child in self.children)


class Or(BinOp):
    operator = "∨"

    def eval(self, v):
        return any(child.eval(v) for child in self.children)


class Not(Formula):
    def __init__(self, child):
        self.child = child

    def eval(self, v):
        return not self.child.eval(v)

    def __str__(self):
        return "¬" + str(self.child)

    __repr__ = __str__

    def eq(self, other):
        return self.child == other.child


class Variable(Formula):
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def eval(self, v):
        return self in v

    def __str__(self):
        return str(self.name)

    __repr__ = __str__

    def eq(self, other):
        return self.name == other.name
