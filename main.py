import cmd
import os
from timeit import default_timer

import parser
from heuristics.bc_fanin import bc_fanin
from heuristics.fanin import fanin
from heuristics.random import random_order


class MyCLI(cmd.Cmd):
    prompt = ">> "
    intro = """Welcome to MyCLI. Type "help" for available commands.
        Type "list" for available input files.
        Type "choose {filename}" to create an ordering from the input file.
        Type "quit" to quit.
        """

    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()

    def do_list(self, line):
        """List files and directories in the current directory."""
        files_and_dirs = os.listdir(self.current_directory + r"\\input_files")
        for item in files_and_dirs:
            print(item)

    def do_choose(self, line):
        """Choose the input file to create a variable ordering"""
        path = self.current_directory + r"\\input_files\\" + line
        with open(path, "r") as file:
            start_time = default_timer()
            try:
                formula = parser.load(file)
            except parser.ParserWarning as e:
                print(f"Warning: {e}. Please try again.")
                return
            parsed_time = default_timer()
            print(
                "the formula: "
                + str(formula)
                + " has been parsed in "
                + str(parsed_time - start_time)
                + " seconds."
            )
            # TODO assess which heuristic to call given whether it is SAT, CNF
            #  or BC input
            # order = random_order(formula)
            # order = fanin(formula)
            order = bc_fanin(formula)
            end_time = default_timer()
            print(
                "The order: "
                + order
                + " has been decided in "
                + str(end_time - parsed_time)
                + " seconds."
            )
            file.close()

    def do_quit(self, line):
        """Exit the CLI."""
        return True


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    MyCLI().cmdloop()
