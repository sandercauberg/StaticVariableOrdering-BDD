import os

import pandas as pd

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

rows = []

commands = commands_dict[chosen_input]

# Iterate over the files in the folder
for file_name in sorted(os.listdir(folder_path)):
    file_path = os.path.join(folder_path, file_name)
    bdd = None
    file_row = [file_name, "", "", "", ""]
    # We do not want to include sub-folders and files, so we check if it is a file
    if os.path.isfile(file_path):
        # Apply the list of commands to the current file
        for command_index, command in enumerate(commands):
            try:
                formatted_command = command.format(file_path)
                # Execute the command with the file name as an argument
                result_dict = main.MyCLI.do_choose(my_cli, formatted_command, bdd=bdd)
                bdd = dict(
                    tree=result_dict["Result"]["BDD Info"]["BDD"]["tree"],
                    roots=result_dict["Result"]["BDD Info"]["BDD"]["roots"],
                )
                if (
                    command_index == 0
                ):  # Only fill in these columns for the first command
                    print("COMMAND index 0, formatted command:", formatted_command)
                    file_row = [
                        file_name,
                        result_dict["Result"]["Parsing Time"],
                        result_dict["Result"]["BDD Info"]["Original BDD creation time"],
                        result_dict["Result"]["BDD Info"]["Original BDD size"],
                        result_dict["Result"]["BDD Info"][
                            "Original BDD # of satisfying assignments"
                        ],
                    ]

                file_row.extend(
                    [
                        command,
                        result_dict["Factor_out"]
                        if chosen_input == "CNF" and "transform bc" in formatted_command
                        else "-",
                        result_dict["Result"]["Ordering Time"],
                        result_dict["Result"]["BDD Info"][
                            "Reordered BDD creation time"
                        ],
                        result_dict["Result"]["BDD Info"]["Reordered BDD size"],
                        result_dict["Result"]["BDD Info"][
                            "Reordered BDD # of satisfying assignments"
                        ],
                    ]
                )
            except Exception as e:
                # If an error occurs, add placeholders for the command's columns
                file_row.extend([command + str(e), "", "", "", "", ""])
        # Append the file_row list to the rows list
        rows.append(file_row)

# Define the column names for the DataFrame
columns = [
    "File",
    "Parsing Time",
    "Original BDD Creation Time",
    "Original BDD Size",
    "Original BDD # of satisfying assignments",
]

# Add columns for each command result
for command_index in range(len(commands)):
    columns.extend(
        [
            f"Command {command_index+1}",
            f"Factor out {command_index+1}",
            f"Ordering Time {command_index+1}",
            f"Reordered BDD creation time {command_index+1}",
            f"Reordered BDD size {command_index+1}",
            f"Reordered BDD # of satisfying assignments {command_index+1}",
        ]
    )

# Create the DataFrame from the list of rows and columns
df = pd.DataFrame(rows, columns=columns)

# Write the DataFrame to a CSV file
csv_file_path = "benchmark_results.csv"
df.to_csv(csv_file_path, index=False)
