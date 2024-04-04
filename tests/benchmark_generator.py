import os
import polars as pl

import main

# Define the list of commands to apply to each file
commands = [
    "{}",
    "{} -heuristic fanin",
    "{} -transform bc",
    "{} -transform bc -heuristic weight",
    "{} -transform bc -heuristic fanin",
    "{} -transform bc -heuristic dependent",
]

# Specify the folder containing the files
folder_path = os.path.abspath("../input_files/benchmark_test")
my_cli = main.MyCLI()

# Create an empty Polars DataFrame to store the results
schema = [("File", str), ("Command", str), ("Result", str)]
df = pl.DataFrame([], schema=schema)

# Iterate over the files in the folder
for file_name in sorted(os.listdir(folder_path)):
    file_path = os.path.join(folder_path, file_name)
    if os.path.isfile(file_path):
        # Apply the list of commands to the current file
        for command in commands:
            try:
                formatted_command = command.format(file_path)
                # Execute the command with the file name as an argument
                result_dict = main.MyCLI.do_choose(my_cli, formatted_command)
                # Append the result to the main DataFrame
                df = pl.concat(
                    [
                        df,
                        pl.DataFrame(
                            [
                                (
                                    result_dict["File"],
                                    result_dict["Command"],
                                    result_dict["Result"],
                                )
                            ],
                            schema=schema,
                        ),
                    ]
                )
            except Exception as e:
                # If an error occurs, set the corresponding values in the DataFrame to "Error"
                df = pl.concat(
                    [df, pl.DataFrame([(file_name, command, "Error")], schema=schema)]
                )

# Write the DataFrame to a CSV file
csv_file_path = "benchmark_results.csv"
df.write_csv(csv_file_path)
