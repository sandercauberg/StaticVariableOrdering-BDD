import os
import parser
import tempfile

import circuitgraph
import pytest

from meta.circuit import CustomCircuit


@pytest.mark.parametrize(
    "input_string,expected_output",
    [
        (
            "c Sample SAT format\nc\np sat 4\n (*(+(1 3 -4)\n +(4)\n +(2 3)))",
            "((1 ∨ 3 ∨ ¬4) ∧ (4) ∧ (2 ∨ 3))",
        ),
        (
            "c Sample SAT format\nc\np sat 4\n (*(+(1 3-4)\n +(4)\n +(2 3)))",
            "((1 ∨ 3 ∨ ¬4) ∧ (4) ∧ (2 ∨ 3))",
        ),
    ],
)
def test_input_file_basic__sat(input_string, expected_output):
    """Test a basic correct input, while also testing leaving out some
    unambiguous spacing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(input_string)
        temp_file_path = temp_file.name

    try:
        input_format, formula = parser.load(temp_file_path)

        assert input_format == "sat"
        assert str(formula) == expected_output
    finally:
        # Clean up the temporary file
        if temp_file_path:
            os.remove(temp_file_path)


def test_input_file_basic__cnf():
    """Test a basic correct cnf input, taken into account a random
    ordering within the clauses."""
    text = "c Example CNF format file\nc\np cnf 4 3\n1 3 -4 0\n4 0 2\n-3"

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(text)
        temp_file_path = temp_file.name

    try:
        input_format, formula = parser.load(temp_file_path)

        expected_output_clauses = [{"2", "¬3"}, {"1", "3", "¬4"}, {"4"}]
        actual_output_clauses = [
            {str(variable) for variable in child.children} for child in formula.children
        ]

        assert input_format == "cnf"
        for expected_clause in expected_output_clauses:
            assert expected_clause in actual_output_clauses
    finally:
        # Clean up the temporary file
        if temp_file_path:
            os.remove(temp_file_path)


@pytest.mark.parametrize(
    "input_string,error_string",
    [
        (
            "c Sample SAT format\nc\np\n (*(+(1 3 -4)\n +(4)\n +(2 3)))",
            "Couldn't find a problem line before an unknown kind of line",
        ),
        (
            "c Sample SAT format\nc\n (*(+(1 3 -4)\n +(4)\n +(2 3)))",
            "Couldn't find a problem line before an unknown kind of line",
        ),
        (
            "c Sample SAT format\nc\npj\n (*(+(1 3 -4)\n +(4)\n +(2 3)))",
            "Couldn't find a problem line before an unknown kind of line",
        ),
        ("", "Couldn't find a problem line before the end of the file"),
        (
            "c Sample SAT format\nc\np test 4\n (*(+(1 3 -4)\n +(4)\n +(2 3)))",
            "Unknown format 'test'",
        ),
        (
            "c Sample SAT format\nc\np \n (*(+(1 3 -4)\n +(4)\n +(2 3)))",
            "Malformed problem line",
        ),
        (
            "c Sample SAT format\nc\np sat 4\n (*(+(1 3 -4(\n +(4)\n +(2 3)))",
            "Found unexpected token '4('",
        ),
        (
            "c Sample SAT format\nc\np sat\n (*(+(1 3 * -4)\n +(4)\n +(2 3)))",
            "Found unexpected token '*'",
        ),
        (
            "c Sample SAT format\nc\np sat 4\n (*(+(1 3 -4)\n +(4)\n +(2 3))",
            "Unexpected end of tokens after opening parenthesis",
        ),
        (
            "c Sample SAT format\nc\np sat 4\n (*(+(1 3 -4 (\n +(4)\n +(2 3)))",
            "Expected closing paren, found '+('",
        ),
        (
            "c Sample SAT format\nc\np sat 4\n (*(+(1 3 -4)\n -+(4)\n +(2 3)))",
            "Only variables can be negated, not (4)",
        ),
        (
            "c Example CNF format file\nc\np cnf 4 3\n1 3 -4 0\n+(4) 0 2\n-3",
            "Found unexpected token '+(4)'",
        ),
    ],
)
def test_input_file__error(input_string, error_string):
    with pytest.raises(parser.ParserWarning) as e:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_file.write(input_string)
            temp_file_path = temp_file.name

        try:
            parser.load(temp_file_path)
        finally:
            # Clean up the temporary file
            if temp_file_path:
                os.remove(temp_file_path)

    assert str(e.value) == error_string


@pytest.mark.parametrize(
    "input_string,expected_output",
    [
        (
            (
                "BC1.1\nVAR A;\nVAR B;\nVAR C;\nVAR D;\nAND GATE AND1 A B;\nOR GATE OR1"
                " AND1 C;\nNOT GATE NOT1 D;\nASSIGN OUTPUT OR1;"
            ),
            10,
        ),
        (
            (
                "BC1.1\nVAR A;\nVAR B;\nVAR C;\nVAR D;\nAND GATE AND1 A B;\nOR GATE OR1"
                " AND1 C;\nNOT GATE NOT1 D;\nAND GATE AND2 OR1 NOT1;\nASSIGN OUTPUT"
                " AND2;"
            ),
            5,
        ),
        (
            (
                "BC1.1\nVAR A;\nVAR B;\nVAR C;\nVAR D;\nVAR E;\nVAR F;\n\nOR GATE OR1 A"
                " B;\nAND GATE AND1 C D;\nOR GATE OR2 E F;\nOR GATE OR3 OR1 AND1;\nOR"
                " GATE OR4 AND1 OR2;\nOR GATE OR5 OR4 F;\nAND GATE AND2 AND1 OR5;\nNOR"
                " GATE NOR1 OR3 AND2;\nASSIGN OUTPUT NOR1;\n"
            ),
            12,
        ),
        (
            (
                "BC1.1\nVAR A;\nVAR B;\nAND GATE AND1 A B;\nNAND GATE NAND1 A B;\nAND"
                " GATE AND2 AND1 NAND1;\nASSIGN OUTPUT AND2;\n"
            ),
            0,
        ),
    ],
)
def test_input_file_basic__bc(input_string, expected_output):
    """Test a basic correct bc input, while also testing leaving out some
    unambiguous spacing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write(input_string)
        temp_file_path = temp_file.name

    try:
        input_format, circuit = parser.load(temp_file_path)

        assert input_format == "bc"
        assert isinstance(circuit, CustomCircuit)
        assert (
            circuitgraph.sat.model_count(
                circuit, assumptions={output: True for output in circuit.outputs()}
            )
            == expected_output
        )
    finally:
        # Clean up the temporary file
        if temp_file_path:
            os.remove(temp_file_path)


@pytest.mark.parametrize(
    "input_string,expected_output",
    [
        (
            (
                "module c17 (N1,N2,N3,N6,N7,N22,N23);\n\ninput"
                " N1,N2,N3,N6,N7;\n\noutput N22,N23;\n\nwire N10,N11,N16,N19;\n\nnand"
                " NAND2_1 (N10, N1, N3);\nnand NAND2_2 (N11, N3, N6);\nnand NAND2_3"
                " (N16, N2, N11);\nnand NAND2_4 (N19, N11, N7);\nnand NAND2_5 (N22,"
                " N10, N16);\nnand NAND2_6 (N23, N16, N19);\n\nendmodule"
            ),
            13,
        ),
    ],
)
def test_input_file_basic_verilog(input_string, expected_output):
    """Test input and reading of verilog files. This example has multiple outputs."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".v") as temp_file:
        temp_file.write(input_string)
        temp_file_path = temp_file.name

    try:
        input_format, circuit = parser.load(temp_file_path)

        assert input_format == "v"
        assert isinstance(circuit, circuitgraph.Circuit)
        assert len(circuit.outputs()) == 2
        assert (
            circuitgraph.sat.model_count(
                circuit, assumptions={output: True for output in circuit.outputs()}
            )
            == expected_output
        )
    finally:
        # Clean up the temporary file
        if temp_file_path:
            os.remove(temp_file_path)


@pytest.mark.parametrize(
    "input_string,error_string",
    [
        (
            (
                "BC1.1\nAND GATE AND1 A B;\nOR GATE OR1 AND1 C;\nNOT GATE NOT1"
                " D;\nASSIGN OUTPUT OR1;"
            ),
            "node 'A' does not exist.",
        ),
        (
            (
                "BC1.1\nAND GATE AND1 B A;\nOR GATE OR1 AND1 C;\nNOT GATE NOT1"
                " D;\nASSIGN OUTPUT OR1;"
            ),
            "node 'B' does not exist.",
        ),
        (
            (
                "BC1.1\nVAR A;\nVAR B;\nVAR C;\nVAR D;\nAND GATE AND1 A B;\nOR GATE OR1"
                " AND1 C;\nNOT GATE NOT1 D;"
            ),
            (
                "No output found in Boolean Circuit. Please assign (an) output(s) with"
                " 'ASSIGN {name} {fanins}'."
            ),
        ),
        (
            "BC1.1",
            (
                "No inputs found in Boolean Circuit. Please assign inputs with 'VAR"
                " {name}'."
            ),
        ),
    ],
)
def test_input_file__bc__error(input_string, error_string):
    with pytest.raises(parser.ParserWarning) as e:
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_file.write(input_string)
            temp_file_path = temp_file.name

        try:
            parser.load(temp_file_path)
        finally:
            # Clean up the temporary file
            if temp_file_path:
                os.remove(temp_file_path)

    assert str(e.value) == error_string
