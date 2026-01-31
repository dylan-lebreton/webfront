from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import cast

from jinja2 import Template

from ..base import Resource


class Icon(Resource):
    _EXT_TO_MIME: dict[str, str] = {
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }

    def __init__(
            self,
            path: str | Path,
            href: str | Path,
            *,
            sizes: str | None = None,
    ):
        super().__init__(path=path, href=href)
        self.rel = "icon"  # imposé
        self.sizes = sizes
        self.type = self._infer_type_from_path(self.path)

    @classmethod
    def _infer_type_from_path(cls, path: Path) -> str | None:
        return cls._EXT_TO_MIME.get(path.suffix.lower())

    def render(self) -> str:
        template_text = (
            resources.files("webfront.resource.icon")
            .joinpath("component.html")
            .read_text(encoding="utf-8")
        )
        template = Template(template_text)

        return cast(
            str,
            template.render(
                rel=self.rel,
                href=str(self.href),
                type=self.type,
                sizes=self.sizes,
            ),
        )
