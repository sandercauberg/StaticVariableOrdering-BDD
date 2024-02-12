from dd import autoref


def create_bdd(formula, var_order):
    # Create BDD with BuDDy
    var_names = [f"var_{var}" for var in formula.extract_variables()]
    formula = (
        str(formula).replace("∨", r" \/ ").replace("∧", r" /\ ").replace("¬", "!")[1:-1]
    )
    for i in range(10):
        formula = formula.replace(str(i), f"var_{i}")

    bdd = autoref.BDD()
    bdd.declare(*var_names)
    u = bdd.add_expr(formula)

    # Print BDD before reordering
    print("BDD Before Reordering:")
    print(bdd)
    print("Number of satisfying assignments: " + str(bdd.count(u)))

    # Set the variable order
    var_names = [f"var_{var}" for var in var_order]
    bdd = autoref.BDD()
    bdd.declare(*var_names)
    bdd.add_expr(formula)

    # Print BDD after reordering
    print("\nBDD After Reordering:")
    print(bdd)
