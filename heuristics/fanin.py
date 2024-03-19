def calculate(formula):
    vars = formula.extract_variables()

    dependencies_list = []
    for variable in vars:
        visited_variables = set()
        dependencies = 0
        visited_variables.add(variable)

        for child in formula.children:
            child_variables = child.extract_variables()
            if variable in child_variables:
                dependencies += len(child_variables - visited_variables)
                visited_variables.update(child_variables)
        dependencies_list.append((variable, dependencies))

    dependencies_list.sort(key=lambda x: x[1], reverse=True)

    # for variable, dependencies in dependencies_list:
    #     print(f'var {variable} has #dependencies {dependencies}')

    result_string = " < ".join(map(lambda x: str(x[0]), dependencies_list))
    result_list = [variable for variable, _ in dependencies_list]

    return result_string, result_list
