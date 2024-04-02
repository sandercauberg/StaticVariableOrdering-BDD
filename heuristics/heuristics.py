heuristics_boolean_circuits = {
    "fanin": "heuristics.bc_fanin",
    "weight": "heuristics.bc_weight_heuristics",
    "dependent": "heuristics.bc_dependent_count",
}

heuristics_cnf = {"fanin": "heuristics.fanin"}

heuristics_sat = {"fanin": "heuristics.fanin"}

heuristics = {
    "bc": heuristics_boolean_circuits,
    "v": heuristics_boolean_circuits,
    "cnf": heuristics_cnf,
    "sat": heuristics_sat,
}
