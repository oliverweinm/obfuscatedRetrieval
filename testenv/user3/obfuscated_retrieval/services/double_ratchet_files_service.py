from obfuscated_retrieval.double_ratchet.double_ratchet_functions import *

class DoubleRatchetFilesService:
    def __init__(self):
        print("DoubleRatchetFilesService.__init__()")
        pass

    def add_to_x3dh_confirmed_list(self, recipient_key):
        already_contained = False
        print(f"add_to_x3dh_confirmed_list({recipient_key})")
        try:
            with open(path_x3dh_confirmed, 'x') as file:
                pass
        except OSError:
            with open(path_x3dh_confirmed, 'rt') as file:
                lines = [line.rsplit()[0] for line in file.readlines()]
                if recipient_key in lines:
                    return
                else:
                    with open(path_x3dh_confirmed, 'a') as file:
                        file.write(recipient_key + os.linesep)
                        return
        with open(path_x3dh_confirmed, 'a') as file:
            file.write(recipient_key + os.linesep)

    def add_x3dh_established(self, recipient_key):
        print(f"add_x3dh_established({recipient_key})")
        already_contained = False
        with open(path_x3dh_established, 'rt') as x3dh_established_file:
            lines = [line.rsplit()[0] for line in x3dh_established_file.readlines()]
            print(f"   lines: {lines}")
            already_contained = recipient_key in lines
            pass
        print("   already_contained: ", already_contained)
        if not already_contained:
            with open(path_x3dh_established, 'a') as x3dh_established_file:
                x3dh_established_file.write(recipient_key + os.linesep)
                pass

    def is_x3dh_outstanding(self, recipient_key):
        print(f"is_x3dh_outstanding({recipient_key})")
        with open(path_x3dh_outstanding, 'rt') as x3dh_outstanding_file:
            lines = [line.rsplit()[0] for line in x3dh_outstanding_file.readlines()]
        return recipient_key in lines

    def is_x3dh_established(self, recipient_key):
        print(f"is_x3dh_established({recipient_key})")
        with open(path_x3dh_established, 'rt') as x3dh_established_file:
            lines = [line.rsplit()[0] for line in x3dh_established_file.readlines()]
            print(lines)
        return (recipient_key in lines or str(recipient_key) in lines)

    def is_x3dh_confirmed(self, recipient_key):
        print(f"is_x3dh_confirmed({recipient_key})")
        with open(path_x3dh_confirmed, 'rt') as x3dh_confirmed_file:
            lines = [line.rsplit()[0] for line in x3dh_confirmed_file.readlines()]
        return recipient_key in lines

    def is_x3dh_started(self, recipient_key):
        print(f"is_x3dh_started({recipient_key})")
        try:
            if self.is_x3dh_outstanding(recipient_key) \
                or self.is_x3dh_established(recipient_key) \
                or self.is_x3dh_confirmed(recipient_key):
                print("True")
                return True
            else:
                print("False")
                return False
        except FileNotFoundError as fnfe:
            print("False")
            return False


    def get_x3dh_confirmed_list(self):
        with open(path_x3dh_confirmed, 'rt') as x3dh_confirmed_file:
            count = [line.rsplit()[0] for line in x3dh_confirmed_file.readlines()]
            return count, len(count)
