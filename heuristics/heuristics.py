heuristics_boolean_circuits = {
    "fanin": "heuristics.bc_fanin",
    "fanin2": "heuristics.bc_fanin2",
    "weight": "heuristics.bc_weight_heuristics",
    "dependent": "heuristics.bc_weight_heuristics",
}

heuristics_cnf = {"fanin": "heuristics.fanin"}

heuristics_sat = {"fanin": "heuristics.fanin"}

heuristics = {
    "bc": heuristics_boolean_circuits,
    "v": heuristics_boolean_circuits,
    "cnf": heuristics_cnf,
    "sat": heuristics_sat,
}
