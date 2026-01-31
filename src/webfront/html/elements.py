from abc import ABC
from typing import List

from typeguard import typechecked

from . import attributes as attrs
from ..renderable import Renderable


@typechecked
class Element(Renderable, ABC):
    pass


@typechecked
class AttributedElement(Element, ABC):
    """
    Base class that renders all attributes found on self
    that are instances of Attribute.
    """

    def render_attributes(self) -> str:
        rendered: list[str] = []

        for value in self.__dict__.values():
            if isinstance(value, attrs.Attribute):
                rendered.append(value.render())

        if not rendered:
            return ""

        return " " + " ".join(rendered)


@typechecked
class ContainerElement(Element, ABC):
    def __init__(self, children: List[Element] | None = None) -> None:
        self.children: List[Element] = children or []

    def render_children(self) -> str:
        return "".join(child.render() for child in self.children)


@typechecked
class DocType(Element):

    def render(self) -> str:
        return "<!DOCTYPE html>"


@typechecked
class HTML(ContainerElement, AttributedElement):

    def __init__(
            self,
            lang: attrs.Lang | None = None,
            dir_: attrs.Dir | None = None,
            children: List[Element] | None = None,
    ) -> None:
        super().__init__(children=children)
        self.lang = lang
        self.dir = dir_

    def render(self) -> str:
        return f"<html{self.render_attributes()}>{self.render_children()}</html>"


@typechecked
class Head(ContainerElement):

    def render(self) -> str:
        return f"<head>{self.render_children()}</head>"


@typechecked
class Body(ContainerElement):
    def render(self) -> str:
        return f"<body>{self.render_children()}</body>"


@typechecked
class Title(Element):
    def __init__(self, value: str) -> None:
        self.value = value

    def render(self) -> str:
        return f"<title>{self.value}</title>"


@typechecked
class VoidElement(Element, ABC):
    pass


@typechecked
class MetaElement(VoidElement, AttributedElement):
    def render(self) -> str:
        return f"<meta{self.render_attributes()}>"


@typechecked
class MetaCharset(MetaElement):
    """
    <meta charset="...">
    """

    def __init__(self, charset: attrs.Charset) -> None:
        self.charset = charset


@typechecked
class MetaViewport(MetaElement):
    """
    <meta name="viewport" content="...">
    """

    def __init__(self, name: attrs.Name, content: attrs.Content) -> None:
        self.name = name
        self.content = content


@typechecked
class Link(VoidElement, AttributedElement):
    def render(self) -> str:
        return f"<link{self.render_attributes()}>"


@typechecked
class LinkIcon(Link):
    """
    <link rel="icon" href="..." type="..." sizes="...">
    """

    def __init__(
            self,
            rel: attrs.Rel,
            href: attrs.Href,
            type_: attrs.Type | None = None,
            sizes: attrs.Sizes | None = None,
    ) -> None:
        self.rel = rel
        self.href = href
        self.type = type_
        self.sizes = sizes
