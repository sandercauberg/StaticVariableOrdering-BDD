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
        raise NotImplementedError("Plain formula can not be evaluated")

    def is_cnf(self):
        return (
            isinstance(self, And)
            and all(isinstance(child, Or) for child in self.children)
            and all(
                (isinstance(var, Variable) for var in child.children)
                for child in self.children
            )
        )

    def is_dnf(self):
        return (
            isinstance(self, Or)
            and all(isinstance(child, And) for child in self.children)
            and all(
                (isinstance(var, Variable) for var in child.children)
                for child in self.children
            )
        )

    def extract_variables(self):
        variables = []
        seen_variables = set()  # To track variables that have been added already

        def add_variable(var):
            if var not in seen_variables:
                variables.append(var)
                seen_variables.add(var)

        if isinstance(self, Variable):
            add_variable(self)
        elif isinstance(self, BinOp):
            for child in self.children:
                for var in child.extract_variables():
                    add_variable(var)
        elif isinstance(self, Not):
            for var in self.child.extract_variables():
                add_variable(var)

        return variables

    def extract_negated_variables(self):
        negated_variables = set()
        if isinstance(self, Not) and isinstance(self.child, Variable):
            negated_variables.add(self.child)
        elif isinstance(self, BinOp):
            for child in self.children:
                negated_variables.update(child.extract_negated_variables())
        elif isinstance(self, Not):
            negated_variables.update(self.child.extract_negated_variables())
        return negated_variables


class BinOp(Formula):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        return "(" + " {} ".format(self.operator).join(map(str, self.children)) + ")"

    __repr__ = __str__

    @property
    def ordered_children(self):
        return list(self.children)

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

    def __hash__(self):
        return hash(("Not", self.child))

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
