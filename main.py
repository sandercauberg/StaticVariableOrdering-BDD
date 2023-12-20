import cmd
import os

import parser
from meta.formula import Variable
from meta.useformula import dop


class MyCLI(cmd.Cmd):
    prompt = ">> "  # Change the prompt text
    intro = (
        'Welcome to MyCLI. Type "help" for available commands. Type "list" '
        'for available input files. Type "hello" to see a message. Type '
        '"quit" to quit.'
        # Your intro message
    )

    def __init__(self):
        super().__init__()
        self.current_directory = os.getcwd()

    def do_list(self, line):
        """List files and directories in the current directory."""
        files_and_dirs = os.listdir(self.current_directory + r"\\input_files")
        for item in files_and_dirs:
            print(item)

    def do_choose(self, line):
        path = self.current_directory + r"\\input_files\\" + line
        with open(path, "r") as file:
            formula = parser.load(file)
            print(formula)
            file.close()

    def do_hello(self, line):
        """Print a greeting."""
        a = Variable("a")
        b = Variable("b")
        c = Variable("c")
        d = Variable("d")

        dop(a | b, {a})
        dop(a & b, {a, b})
        dop(a & b | b & c, {b, c})
        dop((a | c | ~d) & d & (b | ~c), {})
        dop(~a & ~~~b, {})
        dop(a | ~a, {})
        dop((~a | b) | (~b | a), {})
        dop((~a | a) | (~b | b), {})
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        return True


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    MyCLI().cmdloop()
