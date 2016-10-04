from plugins import generic


def register_variants():
    return [Jekyll]


class Jekyll(generic.Generic):
    key_name = "jekyll"

    def register_passes(self):
        generic_passes = generic.Generic.register_passes(self)
        return generic_passes + ['build']

    def build_pass(self, project):
        return self.printer.pexec('build', "jekyll build")
