def fanin(formula):
    vars = formula.extract_variables()

    dependencies_list = []
    for variable in vars:
        dependencies = 0
        for child in formula.children:
            if variable in child.extract_variables():
                dependencies += len(child.extract_variables() - {variable})
        dependencies_list.append((variable, dependencies))

    dependencies_list.sort(key=lambda x: x[1], reverse=True)

    # for variable, dependencies in dependencies_list:
    #     print(f'var {variable} has #dependencies {dependencies}')

    result_string = " < ".join(map(lambda x: str(x[0]), dependencies_list))
    result_list = [variable for variable, _ in dependencies_list]

    return result_string, result_list
