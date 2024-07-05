from meta.circuit import CustomCircuit


def calculate(formula):
    if hasattr(formula, "extract_variables") and callable(
        getattr(formula, "extract_variables")
    ):
        original_order = list(str(x) for x in formula.extract_variables())
    else:
        formula.output_gates = formula.outputs()
        original_order = CustomCircuit.get_ordered_inputs(formula)

    result_string = " < ".join(map(str, original_order))
    result_list = [variable for variable in original_order]

    return result_string, result_list
