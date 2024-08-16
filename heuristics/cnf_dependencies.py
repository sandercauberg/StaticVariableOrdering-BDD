def calculate(formula):
    vars = formula.extract_variables()

    dependencies_list = []
    for variable in vars:
        visited_variables = set()
        dependencies = 0
        visited_variables.add(variable)

        for child in formula.children:
            child_variables = set(child.extract_variables())  # Convert to set
            if variable in child_variables:
                dependencies += len(child_variables - visited_variables)
                visited_variables.update(child_variables)
        dependencies_list.append((variable, dependencies))

    dependencies_list.sort(key=lambda x: x[1], reverse=True)

    result_string = " < ".join(map(str, (x[0] for x in dependencies_list)))
    result_list = [variable for variable, _ in dependencies_list]

    return result_string, result_list
