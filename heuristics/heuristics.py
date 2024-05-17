heuristics_boolean_circuits = {
    "random": "heuristics.random",
    "fanin": "heuristics.bc_fanin",
    "weight": "heuristics.bc_weight_heuristics",
    "dependent": "heuristics.bc_dependent_count",
}

heuristics_cnf = {
    "random": "heuristics.random",
    "dependencies": "heuristics.cnf_dependencies",
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
