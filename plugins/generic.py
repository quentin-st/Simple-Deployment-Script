import os
from utils import stdio


def register_variants():
    return [Generic]


class Generic:
    key_name = "generic"

    def register_passes(self):
        return ['?scss']

    def scss_pass(self):
        # Let's find SCSS files inside this project
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(".scss") and not file.startswith("_"): # Exclude SCSS part files (_part.scss)
                    abs_path = os.path.join(root, file)
                    stdio.ppexec("sass " + abs_path + " " + abs_path.replace(".scss", ".css") + " --style compressed")
