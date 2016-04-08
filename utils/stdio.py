from subprocess import Popen, PIPE, STDOUT
import sys

CRESET = "\033[0m"
CDIM   = "\033[2m"
CBOLD  = "\033[1m"
LGREEN = "\033[92m"
LWARN  = "\033[93m"
LRED   = "\033[91m"


def ppexec(cmd):
    print("    [$ {}]".format(cmd))
    empty_line = bytes()

    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    for line in p.stdout:
        line = line.strip()
        if line == empty_line:
            continue

        try:
            print(CDIM + "    " + line.decode(sys.stdout.encoding) + CRESET)
        except UnicodeDecodeError:
            print(CDIM + "    " + line.decode('windows-1252') + CRESET)
