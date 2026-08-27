from lxml import html
from docxtpl import RichText

from html import unescape
from lxml import html
import re


def tinymce_to_plain_text(value: str) -> str:
    """
    Convert TinyMCE HTML into plain text.

    - removes tags
    - converts HTML entities:
        &ccedil; -> ç
        &aacute; -> á
        &nbsp;   -> space
    - keeps paragraphs and breaks
    """

    if not value:
        return ""

    # Convert entities first
    value = unescape(value)

    # Parse HTML
    root = html.fromstring(
        f"<div>{value}</div>"
    )

    # Extract text while preserving some breaks
    text = root.text_content()

    # Normalize whitespace
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n",
        text,
    )

    return text.strip()

def html_to_richtext(source):
    root = html.fragment_fromstring(
        source or "",
        create_parent=True,
    )

    coverage = get_format_coverage(root)

    remove_bold = coverage["bold"] > 0.9
    remove_italic = coverage["italic"] > 0.9

    rich = RichText()

    def walk(node, bold=False, italic=False):
        tag = node.tag.lower() if isinstance(node.tag, str) else ""

        bold = bold or tag in ("b", "strong")
        italic = italic or tag in ("i", "em")

        # kill global formatting
        if remove_bold:
            bold = False

        if remove_italic:
            italic = False

        if node.text:
            rich.add(
                node.text,
                bold=bold,
                italic=italic,
            )

        for child in node:
            walk(
                child,
                bold=bold,
                italic=italic,
            )

            if child.tail:
                rich.add(
                    child.tail,
                    bold=bold,
                    italic=italic,
                )

    walk(root)

    return rich


def get_format_coverage(root):
    total = 0
    bold = 0
    italic = 0

    def walk(node, b=False, i=False):
        nonlocal total, bold, italic

        tag = node.tag.lower() if isinstance(node.tag, str) else ""

        b = b or tag in ("b", "strong")
        i = i or tag in ("i", "em")

        text = node.text or ""

        length = len(
            "".join(
                c for c in text
                if c.isalnum()
            )
        )

        total += length

        if b:
            bold += length

        if i:
            italic += length

        for child in node:
            walk(child, b, i)

            tail = child.tail or ""

            length = len(
                "".join(
                    c for c in tail
                    if c.isalnum()
                )
            )

            total += length

            if b:
                bold += length

            if i:
                italic += length

    walk(root)

    if total == 0:
        return {
            "bold": 0,
            "italic": 0,
        }

    return {
        "bold": bold / total,
        "italic": italic / total,
    }