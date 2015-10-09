import os
from utils import stdio

def register_variants():
    return [Generic]


class Generic:
    key_name = "generic"

    def register_passes(self):
        return []
