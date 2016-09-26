from subprocess import Popen, PIPE, STDOUT
import sys

CRESET = "\033[0m"
CDIM   = "\033[2m"
CBOLD  = "\033[1m"
LGREEN = "\033[92m"
LWARN  = "\033[93m"
LRED   = "\033[91m"


class Printer:
    colorize = True

    def __init__(self, colorize):
        self.colorize = colorize

    def pprint(self, text=None, color=None):
        if color is not None and self.colorize:
            print(color, text, CRESET)
        elif text is not None:
            print(text)
        else:
            print('')


def ppexec(cmd):
    print("    [$ {}]".format(cmd))
    empty_line = bytes()

    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    for line in p.stdout:
        line = line.strip()
        if line == empty_line:
            continue

        encoding = sys.stdout.encoding

        if encoding is None:
            encoding = 'utf-8'

        try:
            print(CDIM + "    " + line.decode(encoding) + CRESET)
        except (UnicodeEncodeError, UnicodeDecodeError):
            print(CDIM + "    " + line.decode('windows-1252') + CRESET)

    # Wait for process to finish so we can get its return value
    p.wait()
    return p.returncode
