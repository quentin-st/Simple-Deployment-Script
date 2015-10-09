from utils import stdio

def register_variants():
    return [MkDocs]


class MkDocs:
    key_name = "mkdocs"

    def register_passes(self):
        return ['build']

    def build_pass(self):
        stdio.ppexec("mkdocs build --clean")
