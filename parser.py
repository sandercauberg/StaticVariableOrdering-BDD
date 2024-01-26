import collections
import io
import typing

from meta.formula import And, Or, Variable, Not


class ParserWarning(Exception):
    pass


def load(fp: typing.TextIO):
    """Load a sentence from an open file.

    The format is automatically detected.
    """
    for line in fp:
        if line.startswith("c"):
            continue
        if line.startswith("p "):
            problem = line.split()
            if len(problem) < 2:
                raise ParserWarning("Malformed problem line")
            fmt = problem[1]
            if "sat" in fmt or "SAT" in fmt:
                # problem[2] contains the number of variables
                # but that's currently not explicitly represented
                return _load_sat(fp)
            elif "cnf" in fmt or "CNF" in fmt:
                # problem[2] has the number of variables
                # problem[3] has the number of clauses
                return _load_cnf(fp)
            else:
                raise ParserWarning("Unknown format '{}'".format(fmt))
        else:
            raise ParserWarning(
                "Couldn't find a problem line before an unknown kind of line"
            )
    else:
        raise ParserWarning(
            "Couldn't find a problem line before the end of the file"
        )


def loads(s: str):
    """Like :func:`load`, but from a string instead of from a file."""
    return load(io.StringIO(s))


def _load_sat(fp: typing.TextIO):
    tokens = collections.deque()  # type: typing.Deque[str]
    for line in fp:
        if line.startswith("c"):
            continue
        tokens.extend(
            line.replace("(", "( ")
            .replace(")", " ) ")
            .replace("+(", " +(")
            .replace("*(", " *(")
            .replace("-", " - ")
            .split()
        )
    result = _parse_sat(tokens)
    if tokens:
        raise ParserWarning("Found extra tokens past the end of the sentence")
    return result


def _parse_sat(tokens: "typing.Deque[str]"):
    cur = tokens.popleft()
    if cur == "(":
        content = _parse_sat(tokens)
        if not tokens:
            raise ParserWarning(
                "Unexpected end of tokens after opening parenthesis"
            )
        close = tokens.popleft()
        if close != ")":
            raise ParserWarning(
                "Expected closing paren, found {!r}".format(close)
            )
        return content
    elif cur == "-":
        content = _parse_sat(tokens)
        if not isinstance(content, Variable):
            raise ParserWarning(
                "Only variables can be negated, not {!r}".format(content)
            )
        return Not(content)
    elif cur == "*(":
        children = []
        while tokens[0] != ")":
            children.append(_parse_sat(tokens))
        tokens.popleft()
        if children:
            return And(*children)
        else:
            return True
    elif cur == "+(":
        children = []
        while tokens[0] != ")":
            children.append(_parse_sat(tokens))
        tokens.popleft()
        if children:
            return Or(*children)
        else:
            return False
    else:
        return Variable(_parse_int(cur))


def _load_cnf(fp: typing.TextIO):
    tokens = []  # type: typing.List[str]
    for line in fp:
        if line.startswith("c"):
            continue
        tokens.extend(line.replace("-", " -").split())
    return _parse_cnf(tokens)


def _parse_cnf(tokens: typing.Iterable[str]):
    clauses = set()  # type: typing.Set[typing.Tuple[Formula, ...]]
    clause = set()  # type: typing.Set[Formula]
    for token in tokens:
        if token == "0":
            clauses.add(tuple(clause))
            clause = set()
        elif token.startswith("-"):
            clause.add(Not(Variable(_parse_int(token[1:]))))
        else:
            clause.add(Variable(_parse_int(token)))
    if clause:
        # A file may or may not end with a 0
        # Adding an empty clause is not desirable
        clauses.add(tuple(clause))
    sentence = And(*[Or(*clause_tuple) for clause_tuple in clauses])
    return sentence


def _parse_int(token: str) -> int:
    """Parse an integer, or raise an appropriate exception."""
    try:
        return int(token)
    except ValueError:
        raise ParserWarning(
            "Found unexpected token {!r}".format(token)
        ) from None
