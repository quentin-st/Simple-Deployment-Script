import os
from utils import stdio

def register_variants():
    return [Symfony2, Symfony3]


class Symfony:
    def register_passes(self):
        return ['composer', '?assets', 'cache']

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


class Symfony2(Symfony):
    key_name = "symfony2"
    app_console = 'php app/console -n --env=prod'


class Symfony3(Symfony):
    key_name = "symfony3"
    app_console = 'php bin/console -n --env=prod'
