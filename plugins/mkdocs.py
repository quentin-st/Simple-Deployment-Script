from utils import stdio

def register_variants():
    return [MkDocs]


class MkDocs:
    key_name = "mkdocs"

    def register_passes(self):
        return ['build', '?checkout_dash_dash_site']

    def build_pass(self):
        stdio.ppexec("mkdocs build --clean")

    # Put back files originally present in site/ dir and deleted by mkdocs
    def checkout_dash_dash_site_pass(self):
        stdio.ppexec("git checkout -- site")
