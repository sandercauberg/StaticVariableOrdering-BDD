import argparse
import concurrent.futures
import gc
import os

import pandas as pd

from helpers.errors import Timeout
from main import MyCLI

# Define the list of commands to apply to each file, per category
commands_dict = {
    "CNF": [
        "{}",
        "{} -heuristic dependencies",
        # "{} -heuristic mince_manual",
        # "{} -heuristic mince",
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
        "{} -heuristic random",
        "{} -heuristic weight",
        "{} -heuristic fanin",
        "{} -heuristic dependent",
        "{} -transform cnf",
        "{} -transform cnf -heuristic fanin",
        # "{} -transform cnf -heuristic mince_manual",
    ],
}

parser = argparse.ArgumentParser(
    description="Run benchmark script with concurrent jobs option."
)
parser.add_argument(
    "-j", "--jobs", type=int, default=2, help="Number of concurrent jobs"
)
parser.add_argument(
    "-f", "--folder", default="benchmark_test", help="Folder containing the files"
)
parser.add_argument(
    "-c",
    "--category",
    choices=["CNF", "BC"],
    default="BC",
    help="Category (CNF or BC)",
)
args = parser.parse_args()

folder_path = os.path.abspath("input_files/" + args.folder)
chosen_input = args.category
my_cli = MyCLI()

rows = []
bdd_sizes = {}
commands = commands_dict[chosen_input]

with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
    # Iterate over the files in the folder
    for file_name in sorted(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)
        file_row = [file_name, "", "", "", ""]
        # We do not want to include sub-folders and files, so we check if it is a file
        if os.path.isfile(file_path):
            # Apply the list of commands to the current file
            for command_index, command in enumerate(commands):
                try:
                    gc.collect()
                    with Timeout(300):
                        print(command)
                        formatted_command = command.format(file_path)
                        # Execute the command with the file name as an argument
                        result_dict = MyCLI.do_choose(my_cli, formatted_command)
                        if (
                            command_index == 0
                        ):  # Only fill in these columns for the first command
                            file_row = [
                                file_name,
                                result_dict["Result"]["Parsing Time"],
                            ]

                        file_row.extend(
                            [
                                command,
                                result_dict["Factor_out"]
                                if chosen_input == "CNF"
                                and "transform bc" in formatted_command
                                else "-",
                                result_dict["Result"]["Ordering Time"] or "",
                                result_dict["Result"]["BDD Info"]["BDD creation time"] or "",
                                result_dict["Result"]["BDD Info"]["BDD size"] or "",
                            ]
                        )
                        bdd_sizes[(file_name, command)] = result_dict["Result"][
                            "BDD Info"
                        ]["BDD size"]
                except Timeout.Timeout:
                    file_row.extend([command, "Time exceeded", "", "", ""])
                except MemoryError as mem_error:
                    file_row.extend([command, f"Memory error: {mem_error}", "", "", ""])
                    # Handle MemoryError gracefully, log the error if needed
                    # break  # Move to the next file
                except Exception as e:
                    # If an error occurs, add placeholders for the command's columns
                    file_row.extend([command, str(e), "", "", ""])
            # Append the file_row list to the rows list
            rows.append(file_row)

# Define the column names for the DataFrame
columns = [
    "File",
    "Parsing Time","","",""
]

# Add columns for each command result
for command_index in range(len(commands)):
    columns.extend(
        [
            f"Command {command_index+1}",
            f"Factor out {command_index+1}",
            f"Ordering Time {command_index+1}",
            f"BDD creation time {command_index+1}",
            f"BDD size {command_index+1}",
        ]
    )

# Create the DataFrame from the list of rows and columns
df = pd.DataFrame(rows, columns=columns)

# Write the DataFrame to a CSV file
csv_file_path = "benchmark_results.csv"
df.to_csv(csv_file_path, index=False)

bdd_df = pd.DataFrame(bdd_sizes.items(), columns=["File_Command", "BDD Size"])

# Extract file names and commands from the "File_Command" column
bdd_df["File"] = bdd_df["File_Command"].apply(lambda x: x[0])
bdd_df["Command"] = bdd_df["File_Command"].apply(lambda x: x[1])
bdd_df.drop(columns=["File_Command"], inplace=True)

# Pivot the DataFrame to have commands as columns
pivot_df = bdd_df.pivot(index="File", columns="Command", values="BDD Size")

# Write the pivoted DataFrame to a CSV file
csv_file_path_bdd = "bdd_sizes.csv"
pivot_df.to_csv(csv_file_path_bdd)
