import shutil
from pathlib import Path


class Resource:
    def __init__(
            self,
            path: str | Path,
            href: str | Path,
    ):
        self.path = Path(path).resolve().absolute()
        self.href = Path(href)

    def copy(self, website_path: str | Path) -> None:
        website_path = Path(website_path).resolve().absolute()
        destination = (website_path / self.href).resolve().absolute()

        # Prevent path traversal outside website root
        if not destination.is_relative_to(website_path):
            raise ValueError(
                f"Resource href '{self.href}' escapes website root '{website_path}'."
            )

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(self.path, destination)
