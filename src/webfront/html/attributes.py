import re
import threading
import urllib.request
import urllib.request
import xml.etree.ElementTree as ET  # noqa
from abc import ABC, abstractmethod
from typing import Literal

import langcodes
from typeguard import typechecked


class Attribute(ABC):

    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.render()

    def __str__(self) -> str:
        return self.render()


@typechecked
class Lang(Attribute):
    """
    The lang global attribute helps define the language of an element: the language that non-editable elements are
    written in, or the language that the editable elements should be written in by the user.
    The attribute contains a single {{glossary("BCP 47 language tag")}}.

    Note
    ----
    The default value of lang is the empty string, which means that the language is unknown.
    Therefore, it is recommended to always specify an appropriate value for this attribute.
    """

    @staticmethod
    def is_valid_bcp47(tag: str) -> bool:
        try:
            langcodes.Language.get(tag)
            return True
        except langcodes.LanguageTagError:
            return False

    def __init__(self, value: str) -> None:
        # HTML allows lang=""
        if value == "":
            self.value = value
            return

        try:
            language = langcodes.Language.get(value)
            self.value = language.to_tag()  # canonical casing
        except langcodes.LanguageTagError:
            raise ValueError(f"Invalid BCP 47 language tag: {value}")

    def render(self) -> str:
        return f'lang="{self.value}"'


@typechecked
class Dir(Attribute):
    """
    The dir global attribute is an enumerated attribute that indicates the directionality of the element's text.
    """

    def __init__(self, value: Literal["ltr", "rtl", "auto"]) -> None:
        self.value = value

    def render(self) -> str:
        return f'dir="{self.value}"'


@typechecked
class Charset(Attribute):
    """
    The charset attribute declares the character encoding (typically on <meta charset="...">).

    Kept intentionally simple: only allows a small, explicit set.
    Extend the Literal if you need more.
    """

    def __init__(self, value: Literal["utf-8", "latin-1"]) -> None:
        self.value = value

    def render(self) -> str:
        return f'charset="{self.value}"'


@typechecked
class Name(Attribute):
    def __init__(self, value: str) -> None:
        self.value = value

    def render(self) -> str:
        return f'name="{self.value}"'


@typechecked
class Content(Attribute):
    def __init__(self, value: str) -> None:
        self.value = value

    def render(self) -> str:
        return f'content="{self.value}"'


@typechecked
class Rel(Attribute):
    """
    The `rel` attribute defines the relationship between a linked resource and the current document.
    Valid on {{htmlelement('link')}}, {{htmlelement('a')}}, {{htmlelement('area')}}, and {{htmlelement('form')}}.
    The supported values depend on the element on which the attribute is found.

    The type of relationships is given by the value of the `rel` attribute, which, if present, must have a value
    that is an unordered set of unique space-separated keywords.
    """

    def __init__(self, value: str) -> None:
        v = value.strip()
        if v == "":
            raise ValueError("rel cannot be empty")

        tokens = v.split()
        lowered = [t.lower() for t in tokens]

        if len(set(lowered)) != len(lowered):
            raise ValueError(f"rel tokens must be unique (case-insensitive): {value!r}")

        self.value = " ".join(lowered)

    def render(self) -> str:
        return f'rel="{self.value}"'


@typechecked
class Href(Attribute):
    """
    The `href` attribute specifies the URL of the linked resource.

    The exact meaning of the attribute depends on the element on which it is used.
    """

    def __init__(self, value: str) -> None:
        if value == "":
            raise ValueError("href cannot be empty")
        self.value = value

    def render(self) -> str:
        return f'href="{self.value}"'


@typechecked
class Type(Attribute):
    """
    The `type` attribute specifies the media type of the linked resource.

    For {{htmlelement('link')}}, it is the MIME type of the linked resource.
    """

    _IANA_MEDIA_TYPES_XML = "https://www.iana.org/assignments/media-types/media-types.xml"

    # Minimal, practical fallback set (extend if you want)
    _FALLBACK_KNOWN: set[str] = {
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
        "image/avif",
        "image/svg+xml",
        "image/x-icon",
        "text/css",
        "text/javascript",
        "application/javascript",
        "application/json",
        "application/wasm",
        "font/woff",
        "font/woff2",
    }

    _TOKEN_RE = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+$")

    _lock = threading.Lock()
    _iana_mime_types: set[str] | None = None
    _iana_failed: bool = False  # prevent retrying forever if SSL/env is broken

    @classmethod
    def _strip_ns(cls, tag: str) -> str:
        return tag.split("}", 1)[-1]

    @classmethod
    def _try_load_iana_mime_types(cls) -> set[str] | None:
        if cls._iana_mime_types is not None:
            return cls._iana_mime_types
        if cls._iana_failed:
            return None

        with cls._lock:
            if cls._iana_mime_types is not None:
                return cls._iana_mime_types
            if cls._iana_failed:
                return None

            try:
                with urllib.request.urlopen(cls._IANA_MEDIA_TYPES_XML, timeout=10) as resp:
                    xml_bytes = resp.read()
                root = ET.fromstring(xml_bytes)
            except Exception:  # noqa
                cls._iana_failed = True
                return None

            mime_types: set[str] = set()
            current_top: str | None = None
            top_levels = {
                "application", "audio", "font", "image", "message",
                "model", "multipart", "text", "video"
            }

            for elem in root.iter():
                tag = cls._strip_ns(elem.tag)

                if tag == "registry":
                    reg_id = elem.attrib.get("id")
                    if reg_id in top_levels:
                        current_top = reg_id

                elif tag == "record" and current_top is not None:
                    name_elem = None
                    for child in list(elem):
                        if cls._strip_ns(child.tag) == "name":
                            name_elem = child
                            break
                    if name_elem is None:
                        continue

                    subtype = (name_elem.text or "").strip()
                    if subtype:
                        mime_types.add(f"{current_top}/{subtype}".lower())

            if not mime_types:
                cls._iana_failed = True
                return None

            cls._iana_mime_types = mime_types
            return cls._iana_mime_types

    def __init__(self, value: str, strict_registry: bool = False) -> None:
        v = value.strip()
        if v == "":
            raise ValueError("type cannot be empty")

        main, *params = [p.strip() for p in v.split(";")]

        if "/" not in main:
            raise ValueError(f"Invalid media type (missing '/'): {value!r}")

        t, sub = (x.strip() for x in main.split("/", 1))
        if not t or not sub:
            raise ValueError(f"Invalid media type: {value!r}")

        # Basic token validation (good hygiene; avoids garbage)
        if not self._TOKEN_RE.fullmatch(t) or not self._TOKEN_RE.fullmatch(sub):
            raise ValueError(f"Invalid media type token(s): {value!r}")

        candidate = f"{t.lower()}/{sub.lower()}"

        registry = self._try_load_iana_mime_types()
        if registry is not None:
            if candidate not in registry:
                raise ValueError(f"Unknown IANA media type: {candidate!r}")
        else:
            # No registry available (e.g. SSL issues). Either fail hard or use fallback set.
            if strict_registry:
                raise RuntimeError(
                    "IANA media types registry is unavailable (network/SSL). "
                    "Install system CA certificates or set strict_registry=False."
                )
            if candidate not in self._FALLBACK_KNOWN:
                raise ValueError(
                    f"Unknown media type (IANA registry unavailable): {candidate!r}. "
                    "Add it to Type._FALLBACK_KNOWN or fix SSL to enable IANA validation."
                )

        normalized = candidate
        if params:
            normalized += "; " + "; ".join(params)

        self.value = normalized

    def render(self) -> str:
        return f'type="{self.value}"'


@typechecked
class Sizes(Attribute):
    """
    The `sizes` attribute specifies the sizes of icons for visual media.

    It consists of a space-separated list of size values, each consisting of a width and height in pixels,
    or the keyword `any`.
    """

    _SIZE_RE = re.compile(r"^[1-9][0-9]*x[1-9][0-9]*$")

    def __init__(self, value: str) -> None:
        v = value.strip()
        if v == "":
            raise ValueError("sizes cannot be empty")

        if v.lower() == "any":
            self.value = "any"
            return

        tokens = v.split()
        for token in tokens:
            if not self._SIZE_RE.fullmatch(token):
                raise ValueError(f"Invalid sizes token: {token!r}")

        self.value = " ".join(tokens)

    def render(self) -> str:
        return f'sizes="{self.value}"'
