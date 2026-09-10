"""Check the static GitHub Pages site using only Python's standard library.

Usage: python scripts/validate_site.py [--base-url http://127.0.0.1:8765/]
"""

import argparse
import collections
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://gsasec.com.br/"
EMAIL = "giovanni33316@gsasec.com.br"
LINKEDIN = "https://www.linkedin.com/in/giovanni-s-alves/"


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.tags = []
        self.source = path.read_text(encoding="utf-8")
        self.feed(self.source)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def elements(self, name):
        return [attrs for tag, attrs in self.tags if tag == name]

    @property
    def ids(self):
        return [attrs["id"] for _, attrs in self.tags if "id" in attrs]

    @property
    def canonical(self):
        return next((a.get("href") for a in self.elements("link") if a.get("rel") == "canonical"), None)

    @property
    def redirect(self):
        return next((a["data-redirect"] for a in self.elements("body") if "data-redirect" in a), None)


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--base-url", help="Also check local routes and assets over HTTP")
    options = args.parse_args()
    paths = [ROOT / "index.html", *sorted((ROOT / "src").glob("*.html"))]
    pages = {path.resolve(): Page(path) for path in paths}
    errors = []
    refs = set(paths)
    graph = collections.defaultdict(set)

    def check(condition, message):
        if not condition:
            errors.append(message)

    def resolve(page, url):
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            if parsed.netloc != urlsplit(ORIGIN).netloc:
                return None, None
            target = ROOT / unquote(parsed.path).lstrip("/")
        elif parsed.path.startswith("/"):
            target = ROOT / unquote(parsed.path).lstrip("/")
        elif parsed.path:
            target = page.path.parent / unquote(parsed.path)
        else:
            target = page.path
        if target.is_dir():
            target /= "index.html"
        return target.resolve(), unquote(parsed.fragment)

    for path, page in pages.items():
        name = path.relative_to(ROOT).as_posix()
        check(len(page.elements("title")) == 1, f"{name}: expected one title")
        check(len(page.elements("h1")) == 1, f"{name}: expected one H1")
        check(page.elements("html")[0].get("lang") == "pt-BR", f"{name}: invalid language")
        check(sum(a.get("name") == "viewport" for a in page.elements("meta")) == 1, f"{name}: viewport missing or duplicated")
        check(sum(a.get("name") == "description" for a in page.elements("meta")) == 1, f"{name}: description missing or duplicated")
        check(len(page.ids) == len(set(page.ids)), f"{name}: duplicate IDs")
        check(EMAIL in page.source and LINKEDIN in page.source, f"{name}: contacts missing")
        check("giovanni33316@gmail.com" not in page.source, f"{name}: old email")
        check(page.canonical is not None, f"{name}: canonical missing")
        for image in page.elements("img"):
            check(bool(image.get("alt")), f"{name}: missing image alternative text")
            check(bool(image.get("width") and image.get("height")), f"{name}: missing image dimensions")
        for anchor in page.elements("a"):
            check(anchor.get("href") not in (None, "", "#"), f"{name}: placeholder link")
            if anchor.get("target") == "_blank":
                check({"noopener", "noreferrer"} <= set(anchor.get("rel", "").split()), f"{name}: external link rel missing")
        for tag, attrs in page.tags:
            for attr in ("href", "src", "data-redirect"):
                if attr not in attrs:
                    continue
                target, fragment = resolve(page, attrs[attr])
                if target is None:
                    continue
                check(target.is_relative_to(ROOT), f"{name}: reference outside site: {attrs[attr]}")
                check(target.is_file(), f"{name}: missing target: {attrs[attr]}")
                if not target.is_file():
                    continue
                refs.add(target)
                if fragment and target in pages:
                    check(fragment in pages[target].ids, f"{name}: missing fragment: {attrs[attr]}")
                if tag == "a" and target in pages:
                    graph[path].add(target)
            for attr in ("aria-controls", "aria-labelledby", "aria-describedby"):
                for identifier in attrs.get(attr, "").split():
                    check(identifier in page.ids, f"{name}: missing ARIA target {identifier}")
        if page.redirect:
            target, _ = resolve(page, page.redirect)
            check(target in pages and not pages[target].redirect, f"{name}: redirect chain or missing target")
            check(any(a.get("name") == "robots" and "noindex" in a.get("content", "") for a in page.elements("meta")), f"{name}: alias should be noindex")
        else:
            expected = ORIGIN + ("" if name == "index.html" else name)
            check(page.canonical == expected, f"{name}: canonical does not match route")
            for field in ("og:title", "og:description", "og:url", "og:type"):
                check(any(a.get("property") == field and a.get("content") for a in page.elements("meta")), f"{name}: missing {field}")
            check(any(a.get("src", "").split("?")[0].endswith("js/main.js") and "defer" in a for a in page.elements("script")), f"{name}: shared JS missing")

    reachable = set()
    pending = [(ROOT / "index.html").resolve()]
    while pending:
        page = pending.pop()
        if page not in reachable:
            reachable.add(page)
            pending.extend(graph[page] - reachable)
    public_pages = {path for path, page in pages.items() if not page.redirect}
    check(public_pages <= reachable, "Some public pages cannot be reached from the home page")
    sitemap = ET.parse(ROOT / "sitemap.xml")
    locations = [item.text for item in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    expected = {pages[path].canonical for path in public_pages}
    check(set(locations) == expected and len(locations) == len(expected), "Sitemap does not match the canonical public routes")
    check("Sitemap: " + ORIGIN + "sitemap.xml" in (ROOT / "robots.txt").read_text(), "robots.txt does not reference sitemap")

    if options.base_url:
        for path in sorted(refs | {ROOT / "robots.txt", ROOT / "sitemap.xml"}):
            url = urljoin(options.base_url, path.relative_to(ROOT).as_posix())
            try:
                with urlopen(Request(url, method="HEAD"), timeout=10) as response:
                    check(response.status == 200, f"HTTP {response.status}: {url}")
            except Exception as error:
                errors.append(f"HTTP failure: {url}: {error}")
    for error in errors:
        print("FAIL:", error)
    if errors:
        raise SystemExit(1)
    print(f"PASS: {len(pages)} HTML pages, {len(public_pages)} public routes, {len(pages) - len(public_pages)} redirects; links, anchors, assets, contacts, accessibility references, SEO and sitemap.")
    if options.base_url:
        print(f"PASS: HTTP checks for {len(refs | {ROOT / 'robots.txt', ROOT / 'sitemap.xml'})} local resources.")


if __name__ == "__main__":
    main()
