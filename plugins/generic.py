import os
from utils import stdio


def register_variants():
    return [Generic]


class Generic:
    key_name = "generic"

    def register_passes(self):
        return ['?composer', '?npm', '?bower', '?scss', '?gulp']

    def composer_pass(self, project):
        if os.path.isfile("composer.phar"):
            composercmd = "php composer.phar"
        else:
            composercmd = "composer"

        return stdio.ppexec(composercmd + " -n install --optimize-autoloader --no-ansi")

    def bower_pass(self, project):
        return stdio.ppexec("bower install --allow-root")

    def scss_pass(self, project):
        # Let's find SCSS files inside this project
        from_dir = os.getcwd()

        # If project type is symfony, only look for files in src/
        project_type = project['conf'].get("projectType", "generic")
        if project_type == 'symfony2' or project_type == 'symfony3':
            from_dir = os.path.join(from_dir, 'src')

        return_code = 0

        for root, dirs, files in os.walk(from_dir):
            for file in files:
                if file.endswith(".scss") and not file.startswith("_"):  # Exclude SCSS part files (_part.scss)
                    abs_path = os.path.join(root, file)
                    command = "sass {} {} --style compressed".format(abs_path, abs_path.replace('.scss', '.css'))
                    e = stdio.ppexec(command)

                    if e != 0:
                        return_code = e

        return return_code

    def gulp_pass(self, project):
        return stdio.ppexec("gulp")

    def npm_pass(self, project):
        return stdio.ppexec("npm install")
