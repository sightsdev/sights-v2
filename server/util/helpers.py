import os
from typing import override

from fastapi.staticfiles import StaticFiles


class SinglePageApplication(StaticFiles):
    index: str

    def __init__(self, directory: str, index: str = "index.html") -> None:
        self.index = index
        super().__init__(directory=directory, packages=None, html=True, check_dir=True)

    @override
    def lookup_path(self, path: str) -> tuple[str, os.stat_result | None]:
        full_path, stat_result = super().lookup_path(path)
        # if a file cannot be found
        if stat_result is None:
            return super().lookup_path(self.index)
        return full_path, stat_result
