import collections
import io
import typing

from meta.boolean_circuit import Circuit
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
                return "sat", _load_sat(fp)
            elif "cnf" in fmt or "CNF" in fmt:
                # problem[2] has the number of variables
                # problem[3] has the number of clauses
                return "cnf", _load_cnf(fp)
            else:
                raise ParserWarning("Unknown format '{}'".format(fmt))
        elif line.strip() == "BC1.1":
            return "bc", _load_bc(fp)
        elif "module" in line.strip():
            return "v", _load_verilog(fp)
        else:
            raise ParserWarning(
                "Couldn't find a problem line before an unknown kind of line"
            )
    else:
        raise ParserWarning("Couldn't find a problem line before the end of the file")


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
            raise ParserWarning("Unexpected end of tokens after opening parenthesis")
        close = tokens.popleft()
        if close != ")":
            raise ParserWarning("Expected closing paren, found {!r}".format(close))
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
        raise ParserWarning("Found unexpected token {!r}".format(token)) from None


def _load_bc(fp: typing.TextIO):
    circuit = Circuit()

    for line in fp:
        line = line.strip()
        if not line or line.startswith("c"):
            continue  # Skip comments and empty lines

        parts = line.strip().split()
        if parts[0] == "BC1.1":
            continue  # Skip the header line
        if parts[0] == "VAR":
            circuit.add_input(parts[1].rstrip(";"))
        elif parts[1] == "GATE":
            gate_name = parts[2]
            operation = parts[0]
            input_names = [name.rstrip(";") for name in parts[3:]]
            circuit.add_gate(gate_name, operation, input_names)
        elif parts[0] == "ASSIGN":
            output_gate = parts[1]
            circuit.add_output_gate(output_gate, parts[2].rstrip(";"))

    # print(circuit.eval({}))
    # print(circuit.eval({input_name: True for input_name in circuit.inputs}))
    return circuit


def _load_verilog(verilog_code):
    circuit = Circuit()
    verilog_code.seek(0)

    # Read the lines of the file
    verilog_lines = verilog_code.readlines()

    # Set flags to track module start and end
    module_started = False
    module_ended = False

    # Process each line in the Verilog code
    inputs = []
    outputs = []
    for line in verilog_lines:
        line = line.strip()

        # Check for the start of the module
        if line.startswith("module"):
            module_started = True

        # Check for the end of the module
        elif line.startswith("endmodule"):
            module_ended = True
            module_started = False
            if outputs:  # Check if there are any output gates
                for output in outputs:
                    # Find a gate name in circuit.gates
                    gate_name = next(
                        (gate for gate in circuit.gates if output in gate), None
                    )
                    if gate_name is None:
                        raise ValueError(
                            f"No matching gate found for output '{output}'."
                        )
                    circuit.add_output_gate(output, gate_name)

        # Process lines within the module
        elif module_started and not module_ended:
            if line.startswith(("input", "output", "wire")):
                parse_ports(line, inputs, outputs)
            elif line.startswith(("and", "or", "nand", "nor", "xor", "xnor")):
                parse_gate(line, circuit)

    if not module_ended:
        raise ValueError("No module found in Verilog code.")

    [circuit.add_input(input1) for input1 in inputs]
    return circuit


def parse_ports(ports_str, inputs, outputs):
    port_type, port_names = ports_str.split(None, 1)

    port_names = port_names.strip(";")
    port_list = [name.strip() for name in port_names.split(",")]

    if port_type == "input":
        inputs.extend(port_list)
    elif port_type == "output":
        outputs.extend(port_list)


def parse_gate(gate_str, circuit):
    tokens = gate_str.split()
    tokens = tokens[2:]
    gate_name = tokens[0].split("(")[1].strip(",")
    inputs = [token.strip(",);") for token in tokens[1:]]
    gate_type = gate_str.split()[0].lower()
    circuit.add_gate(gate_name, gate_type, inputs)
