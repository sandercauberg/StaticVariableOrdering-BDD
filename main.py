import cmd
import os
import argparse
from timeit import default_timer

import parser
from helpers.buddy_helper import create_bdd

from heuristics.bc_fanin import bc_fanin
from heuristics.bc_weight_heuristics import bc_weight_heuristics
from heuristics.fanin import fanin
from heuristics.random import random_order


class MyCLI(cmd.Cmd):
    prompt = ">> "
    intro = """
        Type "help" for available commands.
        Type "list" for available input files.
        Type "choose {filename}" to create an ordering from the input file.
            Add -dump to dump the BDDs to PNG files.
        Type "quit" to quit.
        """

    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()

    def do_list(self, filename):
        """List files and directories in the current directory."""
        files_and_dirs = os.listdir(self.current_directory + r"\\input_files")
        for item in files_and_dirs:
            print(item)

    def do_choose(self, arg):
        """Choose the input file to create a variable ordering"""
        parse = argparse.ArgumentParser(description="description_ARGPARSE")
        parse.add_argument("filename", help="Name of the input file")
        parse.add_argument("-dump", action="store_true", help="Dump BDDs to PNG files")
        args = parse.parse_args(arg.split())

        filename = args.filename
        dump = args.dump

        path = os.path.join(self.current_directory, "input_files", filename)
        start_time = default_timer()
        try:
            input_format, formula = parser.load(path)
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

        if input_format in ["bc", "v"]:
            # order_string, var_order = bc_fanin(formula)
            # order_string, var_order = random_order(formula)
            order_string, var_order = bc_weight_heuristics(formula)
        else:
            order_string, var_order = random_order(formula)
            order_string, var_order = fanin(formula)

        end_time = default_timer()
        print(
            "The order: "
            + order_string
            + " has been decided in "
            + str(end_time - parsed_time)
            + " seconds."
        )

        create_bdd(input_format, formula, var_order, dump)

    def do_quit(self, line):
        """Exit the CLI."""
        return True


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    MyCLI().cmdloop()
