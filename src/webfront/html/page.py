from typeguard import typechecked

from .elements import DocType, HTML
from ..renderable import Renderable


@typechecked
class Page(Renderable):

    def __init__(self, html_element: HTML) -> None:
        self.children: list[Renderable] = [
            DocType(),
            html_element,
        ]

    def render(self) -> str:
        return "".join(child.render() for child in self.children)
