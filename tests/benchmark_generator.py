import os

import polars as pl

import main

# Define the list of commands to apply to each file, per category
commands_dict = {
    "CNF": [
        "{}",
        "{} -heuristic fanin",
        "{} -transform bc",
        "{} -transform bc -factor_out dependencies",
        "{} -transform bc -heuristic weight",
        "{} -transform bc -factor_out dependencies -heuristic weight",
        "{} -transform bc -heuristic fanin",
        "{} -transform bc -factor_out dependencies -heuristic fanin",
        "{} -transform bc -heuristic dependent",
        "{} -transform bc -factor_out dependencies -heuristic dependent",
    ],
    "BC": [
        "{}",
        "{} -heuristic weight",
        "{} -heuristic fanin",
        "{} -heuristic dependent",
    ],
}

# Specify the folder containing the files
folder_path = os.path.abspath("../input_files/benchmark_test")
chosen_input = "CNF"  # Change this to switch between lists of commands
my_cli = main.MyCLI()

# Create an empty Polars DataFrame to store the results
schema = [
    ("File", str),
    ("Command", str),
    ("Factor_out", str),
    ("Error", str),
    ("Order", str),
    ("Parsing Time", str),
    ("Ordering Time", str),
    ("Original BDD creation time", str),
    ("Original BDD size", str),
    ("Original BDD # of satisfying assignments", str),
    ("Reordered BDD creation time", str),
    ("Reordered BDD size", str),
    ("Reordered BDD # of satisfying assignments", str),
]
df = pl.DataFrame([], schema=schema)

commands = commands_dict[chosen_input]

# Iterate over the files in the folder
for file_name in sorted(os.listdir(folder_path)):
    file_path = os.path.join(folder_path, file_name)
    bdd = None
    # We do not want to include sub-folders and files, so we check if it is a file
    if os.path.isfile(file_path):
        file_data = {"File": file_name}

        # Apply the list of commands to the current file
        for command in commands:
            try:
                formatted_command = command.format(file_path)
                # Execute the command with the file name as an argument
                result_dict = main.MyCLI.do_choose(my_cli, formatted_command, bdd=bdd)
                print("result dict:", result_dict)
                bdd = dict(
                    tree=result_dict["Result"]["BDD Info"]["BDD"]["tree"],
                    roots=result_dict["Result"]["BDD Info"]["BDD"]["roots"],
                )
                # Append the result to the main DataFrame
                df = pl.concat(
                    [
                        df,
                        pl.DataFrame(
                            [
                                (
                                    result_dict["File"],
                                    formatted_command,
                                    result_dict["Factor_out"]
                                    if chosen_input == "CNF"
                                    and "transform bc" in formatted_command
                                    else "-",
                                    "-",
                                    result_dict["Result"]["Order"],
                                    result_dict["Result"]["Parsing Time"],
                                    result_dict["Result"]["Ordering Time"],
                                    result_dict["Result"]["BDD Info"][
                                        "Original BDD creation time"
                                    ],
                                    result_dict["Result"]["BDD Info"][
                                        "Original BDD size"
                                    ],
                                    result_dict["Result"]["BDD Info"][
                                        "Original BDD # of satisfying assignments"
                                    ],
                                    result_dict["Result"]["BDD Info"][
                                        "Reordered BDD creation time"
                                    ],
                                    result_dict["Result"]["BDD Info"][
                                        "Reordered BDD size"
                                    ],
                                    result_dict["Result"]["BDD Info"][
                                        "Reordered BDD # of satisfying assignments"
                                    ],
                                )
                            ],
                            schema=schema,
                        ),
                    ]
                )
            except Exception as e:
                # If an error occurs, show it in the .csv file
                df = pl.concat(
                    [
                        df,
                        pl.DataFrame(
                            [
                                (
                                    file_name,
                                    command,
                                    "",
                                    f"Error: {e}",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                    "",
                                )
                            ],
                            schema=schema,
                        ),
                    ]
                )

# Write the DataFrame to a CSV file
csv_file_path = "benchmark_results.csv"
df.write_csv(csv_file_path)
