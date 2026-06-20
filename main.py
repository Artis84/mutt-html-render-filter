import sys
from urllib.parse import urlparse, parse_qs, unquote
from selectolax.parser import HTMLParser

REMOVE_TAGS = {"script", "style", "noscript", "head", "meta", "link"}

def html_to_text(html: str) -> str:
    tree = HTMLParser(html)

    # remove junk tags
    for tag in REMOVE_TAGS:
        for node in tree.css(tag):
            node.decompose()

    # convert links
    for a in tree.css("a"):
        href = a.attributes.get("href")
        text = a.text(strip=True)

        if href:
            href = clean_url(href)

            if text:
                replacement = f"{text} ({href})"
            else:
                replacement = href

            a.replace_with(replacement)

    # extract text
    root = tree.body or tree
    text = root.text(separator="\n", strip=True)

    # clean whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    return "\n".join(lines)

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

def main():
    html_input = sys.stdin.read()
    print(html_to_text(html_input))


if __name__ == "__main__":
    main()
