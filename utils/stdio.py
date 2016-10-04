from subprocess import Popen, PIPE, STDOUT
import sys
import string

style_none = 0
style_bold = 1
style_underline = 2
style_dim = 2

fg_color_white = 30
fg_color_red = 31
fg_color_green = 32
fg_color_orange = 33

bg_color_default = 40
bg_color_red = 41
bg_color_green = 42
bg_color_orange = 43


class Printer:
    colorize = True
    print_verbose = True

    def __init__(self, colorize, verbose):
        self.colorize = colorize
        self.print_verbose = verbose

    def _print(self, text=None, foreground=None, background=None, style=style_none, line_return=True):
        if text is None:
            sys.stdout.write('')
        elif not self.colorize:
            sys.stdout.write(text)
        else:
            f = str(style)
            if foreground is not None:
                f += ';' + str(foreground)

                if background is not None:
                    f += ';' + str(background)

            sys.stdout.write('\x1b[{}m{}\x1b[0m'.format(f, text))

        if line_return:
            sys.stdout.write('\n')

        sys.stdout.flush()

    def info(self, text, bold=False):
        self._print(
            text=text,
            style=style_none if bold is False else style_bold
        )

    def success(self, text):
        self._print(
            text=text,
            foreground=fg_color_green,
            style=style_bold
        )

    def warning(self, text):
        self._print(
            text=text,
            foreground=fg_color_orange
        )

    def error(self, text):
        self._print(
            text=text,
            foreground=fg_color_red,
            style=style_bold
        )

    def pass_output(self, pass_name, text):
        # Print pass name
        self._print(
            text=' {} '.format(pass_name),
            foreground=fg_color_white,
            background=bg_color_green,
            line_return=False
        )

        # Then print text, with line return
        self._print('  {}'.format(text))

    def verbose(self, text):
        if not self.print_verbose:
            return

        self._print(
            text=text,
            style=style_dim
        )

    def pexec(self, pass_name, cmd):
        self.pass_output(pass_name, "[$ {}]".format(cmd))
        empty_line = bytes()

        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        for line in p.stdout:
            line = line.rstrip()
            if line == empty_line:
                continue

            # Decode command output
            decoded = None
            encodings = [sys.stdout.encoding, 'utf-8', 'windows-1252']

            # Try one encoding at a time
            for encoding in encodings:
                if encoding is None:
                    continue

                try:
                    decoded = line.decode(encoding)
                    break
                except (UnicodeEncodeError, UnicodeDecodeError):
                    # Ignored
                    pass

            if decoded is None:
                decoded = '?'

            # Strip non-printable chars
            decoded = ''.join(filter(lambda x: x in string.printable, decoded))

            self.pass_output(pass_name, decoded)

        # Wait for process to finish so we can get its return value
        p.wait()
        return p.returncode
