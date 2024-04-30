heuristics_boolean_circuits = {
    "fanin": "heuristics.bc_fanin",
    "weight": "heuristics.bc_weight_heuristics",
    "dependent": "heuristics.bc_dependent_count",
}

heuristics_cnf = {
    "fanin": "heuristics.fanin",
    "mince": "heuristics.mince",
    "mince_manual": "heuristics.mince_manual",
}

heuristics_sat = {"fanin": "heuristics.fanin"}

heuristics = {
    "bc": heuristics_boolean_circuits,
    "v": heuristics_boolean_circuits,
    "cnf": heuristics_cnf,
    "sat": heuristics_sat,
}
