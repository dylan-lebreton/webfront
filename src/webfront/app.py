""" import shutil
import webbrowser
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import List

from .page import Page


class App:

    def __init__(
            self,
            path: str | Path,
            index: Page,
            pages: List[Page] | None = None,
    ):
        self.path = Path(path)

        self.index = index
        self.pages = pages if pages is not None else []

    def compile(self, *, overwrite: bool = False) -> None:
        if self.path.exists():
            if not overwrite:
                raise FileExistsError(
                    f"Output directory '{self.path}' already exists. "
                    "Use compile(overwrite=True) to remove it."
                )
            shutil.rmtree(self.path)

        self.path.mkdir(parents=True, exist_ok=False)

        index_path = self.path / "index.html"
        index_path.write_text(
            self.index.render(website_path=self.path),
            encoding="utf-8",
        )

        for page in self.pages:
            page_folder = self.path / page.name
            page_folder.mkdir(parents=True, exist_ok=True)

            page_index_path = page_folder / "index.html"
            page_index_path.write_text(
                page.render(website_path=self.path),
                encoding="utf-8",
            )

    def serve(self, *, port: int = 8000) -> None:
        handler = partial(
            SimpleHTTPRequestHandler,
            directory=str(self.path),
        )

        server = ThreadingHTTPServer(
            ("localhost", port),
            handler,  # noqa
        )

        url = f"http://localhost:{port}"
        print(f"Serving {self.path} at {url}")

        webbrowser.open(url)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
 """