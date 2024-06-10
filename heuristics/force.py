import math
from collections import namedtuple
from parser import ParserWarning

from helpers.cnf2hypergraph import cnf2hypergraph
from meta.formula import Formula
from meta.hypergraph import Hypergraph

# Named tuple for VarInfo
VarInfo = namedtuple("VarInfo", ["sum_cog", "num_occurs"])


def compute_sum_of_spans(graph, idx_of_var):
    sum_spans = 0
    for edge in graph.hyperedges():
        if not edge:
            continue
        indices = [idx_of_var[var] for var in edge]
        sum_spans += max(indices) - min(indices)
    return sum_spans


def calculate(formula):
    if isinstance(formula, Formula) and (formula.is_cnf() or formula.is_dnf()):
        hypergraph = cnf2hypergraph(formula)
    elif isinstance(formula, Hypergraph):
        hypergraph = formula
    else:
        raise ParserWarning("Unknown formula input for FORCE algorithm.")

    result = execute_with_order(hypergraph, hypergraph.nodes())
    result_string = " < ".join(map(lambda x: str(x), result))
    return result_string, result


def execute_with_order(graph, var_of_idx):
    num_vars = len(var_of_idx)
    idx_of_var = {var: idx for idx, var in enumerate(var_of_idx)}

    best_sum_spans = compute_sum_of_spans(graph, idx_of_var)
    best_order = list(var_of_idx)

    num_iterations = int(5 * math.log(num_vars))

    for _ in range(num_iterations):
        infos = [VarInfo(0.0, 0) for _ in range(num_vars)]

        for edge in graph.hyperedges():
            cog_of_edge = sum(idx_of_var[var] for var in edge) / len(edge)
            for var in edge:
                var_idx = idx_of_var[var]
                vi = infos[var_idx]
                infos[var_idx] = VarInfo(vi.sum_cog + cog_of_edge, vi.num_occurs + 1)

        cog_of_var = [
            vi.sum_cog / vi.num_occurs if vi.num_occurs > 0 else 0.0 for vi in infos
        ]

        var_of_idx.sort(key=lambda x: cog_of_var[idx_of_var[x]])
        idx_of_var = {var: idx for idx, var in enumerate(var_of_idx)}

        sum_spans = compute_sum_of_spans(graph, idx_of_var)
        if sum_spans < best_sum_spans:
            best_sum_spans = sum_spans
            best_order = list(var_of_idx)

    return best_order
