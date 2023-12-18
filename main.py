import cmd
import os


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
        files_and_dirs = os.listdir(self.current_directory + r"\input_files")
        for item in files_and_dirs:
            print(item)

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_quit(self, line):
        """Exit the CLI."""
        return True


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    MyCLI().cmdloop()
