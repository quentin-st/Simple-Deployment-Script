import os
from plugins import generic


def register_variants():
    return [Symfony2, Symfony3]


class Symfony(generic.Generic):
    app_console = None

    def __init__(self, printer, cli_args):
        generic.Generic.__init__(self, printer, cli_args)
        self.app_console = self.app_console.replace('__env__', cli_args.env)

        # Define SYMFONY_ENV environment variable for composer post-install commands
        os.environ['SYMFONY_ENV'] = cli_args.env

    def register_passes(self):
        generic_passes = generic.Generic.register_passes(self)
        return generic_passes + ['composer', 'assets', '?assetic', 'cache', '?liip_imagine_cache', '?update_database_schema']

    def assets_pass(self, project):
        return self.printer.pexec('assets', self.app_console + " assets:install --symlink")

    def assetic_pass(self, project):
        return self.printer.pexec('assetic', self.app_console + " assetic:dump")

    def cache_pass(self, project):
        return self.printer.pexec('cache', self.app_console + " cache:clear")

    def liip_imagine_cache_pass(self, project):
        return self.printer.pexec('liip_imagine_cache', self.app_console + " liip:imagine:cache:remove")

    def update_database_schema_pass(self, project):
        return self.printer.pexec('update_database_schema', self.app_console + " doctrine:schema:update --force")


class Symfony2(Symfony):
    key_name = "symfony2"
    app_console = 'php app/console -n --env=__env__'


class Symfony3(Symfony):
    key_name = "symfony3"
    app_console = 'php bin/console -n --env=__env__'
