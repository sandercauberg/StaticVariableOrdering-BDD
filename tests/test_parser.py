import os
import tempfile

import pytest

import parser


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
