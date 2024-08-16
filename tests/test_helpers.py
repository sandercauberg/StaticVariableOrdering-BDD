import os
import parser

import circuitgraph as cg
import pytest

from helpers import cudd_helper
from meta.circuit import CustomCircuit


def get_bdd_from_verilog_file(filename):
    path_name = os.path.join(os.path.dirname(__file__), filename)
    circuit = cg.from_file(path_name)
    bdd, roots = cudd_helper.build_bdd_from_circuit(
        circuit, CustomCircuit.get_ordered_inputs(circuit)
    )
    return bdd, roots


def get_bdd_from_bc_text_file(filename):
    path_name = os.path.join(os.path.dirname(__file__), filename)
    input_format, circuit = parser.load(str(path_name))
    bdd, roots = cudd_helper.build_bdd_from_circuit(
        circuit, CustomCircuit.get_ordered_inputs(circuit)
    )
    return bdd, roots


@pytest.mark.parametrize(
    "testfile,expected_output",
    [
        ("testfiles/c88.v", [2, 2]),
        ("testfiles/5xor.v", [5, 1]),
    ],
)
def test_cudd_helper__build_bdd_verilog(testfile, expected_output):
    bdd, roots = get_bdd_from_verilog_file(testfile)
    assert len(bdd) == expected_output[0]
    assert len(roots) == expected_output[1]


@pytest.mark.parametrize(
    "testfile,expected_output",
    [
        ("testfiles/bc-example.txt", [4, 1]),
        ("testfiles/bc-example2.txt", [5, 1]),
        ("testfiles/bc-example3.txt", [5, 1]),
    ],
)
def test_cudd_helper__build_bdd_bc(testfile, expected_output):
    bdd, roots = get_bdd_from_bc_text_file(testfile)
    assert len(bdd) == expected_output[0]
    assert len(roots) == expected_output[1]


@pytest.mark.parametrize(
    "testfile,expected_output",
    [
        ("testfiles/c88.v", 8),
        ("testfiles/5xor.v", 16),
    ],
)
def test_cudd_helper__count_satisfying_assignments__verilog(testfile, expected_output):
    bdd, roots = get_bdd_from_verilog_file(testfile)
    assignments = cudd_helper.count_satisfying_assignments(bdd, roots)
    assert assignments == expected_output


@pytest.mark.parametrize(
    "testfile,expected_output",
    [
        ("testfiles/bc-example.txt", 10),
        ("testfiles/bc-example2.txt", 5),
        ("testfiles/bc-example3.txt", 12),
    ],
)
def test_cudd_helper__count_satisfying_assignments__bc(testfile, expected_output):
    bdd, roots = get_bdd_from_bc_text_file(testfile)
    assignments = cudd_helper.count_satisfying_assignments(bdd, roots)
    assert assignments == expected_output
