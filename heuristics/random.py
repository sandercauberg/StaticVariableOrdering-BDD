import random


def calculate(formula):
    if hasattr(formula, "extract_variables") and callable(
        getattr(formula, "extract_variables")
    ):
        vars = list(formula.extract_variables())
    else:
        vars = list(formula.inputs())
        formula.inputs = formula.inputs()
        formula.output_gates = formula.outputs()

    random_order = random.sample(vars, len(vars))
    result_string = " < ".join(map(str, random_order))
    result_list = [variable for variable in random_order]

    return result_string, result_list
