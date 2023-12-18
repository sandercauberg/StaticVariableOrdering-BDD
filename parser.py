def read(file):
    text = ""

    for line in file:
        line = line.strip()
        if line.startswith("c"):
            # Comment line
            pass
        elif line.startswith("p"):
            if line.split()[1] == "cnf":
                variables = line.split()[2]
                clauses = line.split()[3]
                print(
                    "cnf with "
                    + variables
                    + " variables and "
                    + clauses
                    + " clauses"
                )
            elif line.split()[1] == "sat":
                variables = line.split()[2]
                print("sat with " + variables + " variables")
        else:
            text = text + line + " "

    output_list = [chunk.strip() for chunk in text.split("0") if chunk.strip()]

    print(output_list)
