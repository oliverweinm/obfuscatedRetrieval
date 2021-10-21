import sneakernet_functions as snf
import sys
import os


class CliSneakernet:
    def __init__(self, PATH, NAME, UPDATE_NR):
        self.path = str(PATH)
        self.user = None
        self.name = str(NAME)
        self.amount_of_files = int(UPDATE_NR)

    def read_path(self):
        self.path = input("PATH: ")

    def get_username(self):
        self.name = input("username: ")

    def login(self):
        self.user = snf.User(self.name, self.path)

    def update_files(self):
        #amount_of_files = int(input("amount: "))
        self.user.exporting(self.amount_of_files)


if __name__ == '__main__':
    n = len(sys.argv)
    print(f"{n} Arguments passed to {sys.argv[0]}")
    cli = CliSneakernet(sys.argv[1], sys.argv[2], sys.argv[3])
    cli.login()
    cli.update_files()
    exit()
    """
    cmd = input(">>> ")
    if cmd == 'path':
        cli.read_path()
    if cmd == 'login':
        cli.get_username()
        cli.login()
    if cmd == 'update':
        cli.update_files()
    """

