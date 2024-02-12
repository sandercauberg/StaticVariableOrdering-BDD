import random


def random_order(formula):
    vars = formula.extract_variables()

    random_order = random.sample(vars, len(vars))
    result_string = " < ".join(map(str, random_order))
    result_list = [variable for variable in random_order]

    return result_string, result_list
