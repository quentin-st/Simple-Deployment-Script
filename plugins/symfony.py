import os
from utils import stdio
from plugins import generic


def register_variants():
    return [Symfony2, Symfony3]


class Symfony(generic.Generic):
    def register_passes(self):
        generic_passes = generic.Generic.register_passes(self)
        return generic_passes + ['composer', 'assets', 'assetic', 'cache', '?liip_imagine_cache', '?update_database_schema']

    def assets_pass(self, project):
        return stdio.ppexec(self.app_console + " assets:install")

    def assetic_pass(self, project):
        return stdio.ppexec(self.app_console + " assetic:dump")

    def cache_pass(self, project):
        return stdio.ppexec(self.app_console + " cache:clear")

    def liip_imagine_cache_pass(self, project):
        return stdio.ppexec(self.app_console + " liip:imagine:cache:remove")

    def update_database_schema_pass(self, project):
        return stdio.ppexec(self.app_console + " doctrine:schema:update --force")


class Symfony2(Symfony):
    key_name = "symfony2"
    app_console = 'php app/console -n --env=prod'


class Symfony3(Symfony):
    key_name = "symfony3"
    app_console = 'php bin/console -n --env=prod'
