import cmd
import os
import argparse
from timeit import default_timer

import parser
from helpers.buddy_helper import create_bdd

from heuristics.bc_fanin import bc_fanin
from heuristics.bc_fanin2 import bc_fanin2
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
            Add -heuristic {heuristic} to choose a specific heuristic.
                Available heuristics for boolean circuits: weight, fanin.
                Available heuristics for cnf/sat: fanin.
                If not specified or non-existing, random ordering will be chosen.
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
        parse.add_argument("-heuristic", help="Choose a specific heuristic")

        try:
            args = parse.parse_args(arg.split())
        except SystemExit:
            return

        path = os.path.join(self.current_directory, "input_files", args.filename)
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
            if args.heuristic == "fanin":
                order_string, var_order = bc_fanin(formula)
            elif args.heuristic == "fanin2":
                order_string, var_order = bc_fanin2(formula)
            elif args.heuristic == "weight":
                order_string, var_order = bc_weight_heuristics(formula)
            else:
                order_string, var_order = random_order(formula)
        else:
            if args.heuristic == "fanin":
                order_string, var_order = fanin(formula)
            else:
                order_string, var_order = random_order(formula)

        end_time = default_timer()
        print(
            "The order: "
            + order_string
            + " has been decided in "
            + str(end_time - parsed_time)
            + " seconds."
        )

        create_bdd(input_format, formula, var_order, args.dump)

    def do_quit(self, line):
        """Exit the CLI."""
        return True


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    MyCLI().cmdloop()
