import os
from utils import stdio


def register_variants():
    return [Symfony2, Symfony3]


class Symfony:
    def register_passes(self):
        return ['composer', '?scss', 'assets', 'cache', '?liip_imagine_cache', '?update_database_schema']

    def composer_pass(self):
        if os.path.isfile("composer.phar"):
            composercmd = "php composer.phar"
        else:
            composercmd = "composer"

        stdio.ppexec(composercmd + " -n install --optimize-autoloader")

    def assets_pass(self):
        stdio.ppexec(self.app_console + " assets:install")
        stdio.ppexec(self.app_console + " assetic:dump")

    def cache_pass(self):
        stdio.ppexec(self.app_console + " cache:clear")

    def liip_imagine_cache_pass(self):
        stdio.ppexec(self.app_console + " liip:imagine:cache:remove")

    def scss_pass(self):
        # Let's find SCSS files inside this project
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if file.endswith(".scss") and not file.startswith("_"): # Exclude SCSS part files (_part.scss)
                    abs_path = os.path.join(root, file)
                    stdio.ppexec("sass " + abs_path + " " + abs_path.replace(".scss", ".css") + " --style compressed")

    def update_database_schema_pass(self):
        stdio.ppexec(self.app_console + " doctrine:schema:update --force")


class Symfony2(Symfony):
    key_name = "symfony2"
    app_console = 'php app/console -n --env=prod'


class Symfony3(Symfony):
    key_name = "symfony3"
    app_console = 'php bin/console -n --env=prod'
