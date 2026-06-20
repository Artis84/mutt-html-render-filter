import sys
from selectolax.parser import HTMLParser
from urllib.parse import urlparse, parse_qs, unquote
BLOCKS = {
    "p", "div", "section", "article",
    "li", "blockquote", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6"
}

REMOVE_TAGS = {"script", "style", "noscript", "head", "meta", "link", "img"}

INLINE_BREAKS = {"br"}

def clean_url(url: str) -> str:
    """
    Unwrap Microsoft SafeLinks / tracking URLs.
    Returns clean destination URL if possible.
    """

    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        # Microsoft SafeLinks pattern
        if "url" in qs:
            real = qs["url"][0]
            return unquote(real)

        return url

    except Exception:
        return url

def iter_children(node):
    child = node.child
    while child:
        yield child
        child = child.next

def render_inline(node):
    if node is None:
        return ""

    # text node
    if node.tag == "-text":
        return node.text()

    # link
    if node.tag == "a":
        text = "".join(render_inline(c) for c in iter_children(node))
        href = clean_url(node.attributes.get("href", ""))

        if href:
            if text:
                return f"{text} ({href})"
            return href

        return text

    # line break
    if node.tag in INLINE_BREAKS:
        return "\n"

    # generic inline/container node
    return "".join(render_inline(c) for c in iter_children(node))

def has_block_ancestor(node):
    parent = node.parent

    while parent:
        if parent.tag in BLOCKS:
            return True
        parent = parent.parent

    return False

def html_to_text(html):
    tree = HTMLParser(html)

    for tag in REMOVE_TAGS:
        for node in tree.css(tag):
            node.decompose()

    root = tree.body or tree

    lines = []

    for node in root.traverse():

        if node.tag not in BLOCKS:
            continue

        if has_block_ancestor(node):
            continue

        text = render_inline(node)

        # collapse whitespace but preserve explicit <br>
        paragraphs = [
            " ".join(part.split())
            for part in text.split("\n")
        ]

        text = "\n".join(p for p in paragraphs if p)

        if text:
            lines.append(text)

    return "\n".join(lines)

def main():
    html_input = sys.stdin.read()
    print(html_to_text(html_input))


if __name__ == "__main__":
    main()
