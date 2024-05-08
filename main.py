import argparse
import cmd
import os
import parser
import time

from helpers.bc2cnf import bc2cnf
from helpers.cnf2bc import cnf2bc
from helpers.cudd_helper import create_bdd
from heuristics import heuristics


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

    def do_choose(self, arg, bdd=None):
        """Choose the input file to create a variable ordering"""
        parse = argparse.ArgumentParser(description="description_ARGPARSE")
        parse.add_argument("filename", help="Name of the input file")
        parse.add_argument("-dump", action="store_true", help="Dump BDDs to PNG files")
        parse.add_argument("-heuristic", help="Choose a specific heuristic")
        parse.add_argument("-transform", help="Choose a transformation process")
        parse.add_argument(
            "-factor_out",
            help="Choose a method for factoring out in transformation process",
        )

        try:
            args = parse.parse_args(arg.split())
        except SystemExit:
            return

        path = os.path.join(self.current_directory, "input_files", args.filename)
        start_time = time.perf_counter()
        try:
            input_format, formula = parser.load(path)
        except parser.ParserWarning as e:
            print(f"Warning: {e}. Please try again.")
            return
        parsed_time = time.perf_counter()
        parsing_time = parsed_time - start_time
        print(
            "the formula: "
            + str(formula)
            + " has been parsed in "
            + str(parsing_time)
            + " seconds."
        )

        heuristic_type = None
        if args.heuristic:
            heuristic_type = args.heuristic

        if input_format not in heuristics.heuristics:
            print(f"No heuristics available for '{input_format}' problem type.")
            return

        # Transformation options
        if args.transform:
            # TODO if more transformations are available, take arguments directly
            if input_format == "cnf" and args.transform == "bc":
                formula = cnf2bc(formula, args.factor_out)
                print(f"Transformed from {input_format} to {args.transform}")
                input_format = "bc"
            elif input_format in ["bc", "v"] and args.transform == "cnf":
                formula = bc2cnf(formula)
                print(f"Transformed from {input_format} to {args.transform}")
                input_format = "cnf"

        heuristic_options = heuristics.heuristics[input_format]

        if heuristic_type in heuristic_options:
            module_path = heuristic_options[heuristic_type]
        elif heuristic_type is None:
            print("No heuristic chosen, using random heuristics.")
            module_path = "heuristics.random"
        else:
            print(
                f"Heuristic '{heuristic_type}' is not available for "
                f"'{input_format}' problem type."
            )
            return

        start_ordering_time = time.perf_counter()
        heuristic_module = __import__(module_path, fromlist=[""])
        order_string, var_order = heuristic_module.calculate(formula)

        end_time = time.perf_counter()
        ordering_time = end_time - start_ordering_time
        print(
            "The order: "
            + order_string
            + " has been decided in "
            + str(ordering_time)
            + " seconds."
        )

        bdd_info = create_bdd(input_format, formula, var_order, bdd=bdd, dump=args.dump)

        return {
            "File": args.filename,
            "Command": f"choose {args.filename}",
            "Factor_out": args.factor_out or "occurrences",
            "Result": {
                "Order": order_string,
                "Parsing Time": parsing_time,
                "Ordering Time": ordering_time,
                "BDD Info": bdd_info,
            },
        }

    def do_quit(self, line):
        """Exit the CLI."""
        return True


if __name__ == "__main__":
    MyCLI().cmdloop()
