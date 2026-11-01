"""Static checks for the site. Standard library only, no build step.

Run from the repo root:
  python3 -m unittest discover -s tests -v
"""

import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://awanninger.com/"
HTML_PAGES = ["index.html", "404.html"]


class Page(HTMLParser):
    """Collects the bits of an HTML page the tests look at."""

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.scripts: list[tuple[dict[str, str | None], str]] = []
        self._script: dict[str, str | None] | None = None
        self._script_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "script":
            self._script, self._script_text = attrs, []

    def handle_data(self, data):
        if self._script is not None:
            self._script_text.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            self.scripts.append((self._script, "".join(self._script_text)))
            self._script = None

    def find(self, tag: str, **attrs: str) -> list[dict[str, str | None]]:
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]


def parse(name: str) -> Page:
    page = Page()
    page.feed((ROOT / name).read_text(encoding="utf-8"))
    return page


def local_path(url: str) -> Path | None:
    """Map a same-site URL to a file in the repo, or None for external URLs."""
    if url.startswith(SITE):
        url = "/" + url[len(SITE):]
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc or url.startswith("#"):
        return None
    path = parsed.path.lstrip("/") or "index.html"
    return ROOT / path


def external_links(page: Page) -> set[str]:
    return {a["href"] for a in page.find("a") if a.get("href", "").startswith(("https://", "mailto:"))}


class TestPages(unittest.TestCase):
    def test_charset_is_first_in_head(self):
        for name in HTML_PAGES:
            html = (ROOT / name).read_text(encoding="utf-8")
            head = html.split("<head>", 1)[1].lstrip()
            self.assertTrue(head.startswith('<meta charset="UTF-8">'), name)

    def test_local_assets_exist(self):
        for name in HTML_PAGES:
            page = parse(name)
            for tag, attrs in page.tags:
                for attr in ("href", "src", "srcset"):
                    url = attrs.get(attr)
                    if not url or (tag == "use" and url.startswith("#")):
                        continue
                    path = local_path(url.split()[0])
                    if path is not None:
                        with self.subTest(page=name, url=url):
                            self.assertTrue(path.is_file(), f"{name}: {url} not found")

    def test_no_inline_scripts_or_styles(self):
        # The Content-Security-Policy allows no 'unsafe-inline'.
        for name in HTML_PAGES:
            page = parse(name)
            for attrs, text in page.scripts:
                if attrs.get("src"):
                    continue
                with self.subTest(page=name):
                    self.assertEqual(attrs.get("type"), "application/ld+json", f"{name}: inline script")
            self.assertFalse(page.find("style"), f"{name}: <style> element")
            for tag, attrs in page.tags:
                self.assertNotIn("style", attrs, f"{name}: style attribute on <{tag}>")
                self.assertFalse(any(k.startswith("on") for k in attrs), f"{name}: inline handler on <{tag}>")

    def test_external_scripts_are_async_or_defer(self):
        for attrs, _ in parse("index.html").scripts:
            if attrs.get("src"):
                self.assertTrue("async" in attrs or "defer" in attrs, attrs["src"])

    def test_new_tab_links_have_noopener(self):
        for a in parse("index.html").find("a"):
            if a.get("target") == "_blank":
                self.assertIn("noopener", (a.get("rel") or "").split(), a["href"])

    def test_icons_are_hidden_from_screen_readers(self):
        for _, attrs in parse("index.html").tags:
            if "icon" in (attrs.get("class") or "").split():
                self.assertEqual(attrs.get("aria-hidden"), "true")

    def test_404_is_noindex(self):
        self.assertTrue(parse("404.html").find("meta", name="robots", content="noindex"))


class TestMetadata(unittest.TestCase):
    page = parse("index.html")

    def meta(self, key: str) -> str:
        found = self.page.find("meta", property=key) or self.page.find("meta", name=key)
        self.assertTrue(found, f"missing meta {key}")
        return found[0]["content"]

    def test_title_and_description_lengths(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", html).group(1).replace("&amp;", "&")
        self.assertLess(len(title), 60)
        self.assertTrue(150 <= len(self.meta("description")) <= 160)

    def test_canonical(self):
        self.assertEqual(self.page.find("link", rel="canonical")[0]["href"], SITE)

    def test_social_tags_filled_and_images_exist(self):
        for key in ["og:type", "og:title", "og:description", "og:url", "og:image", "og:image:width",
                    "og:image:height", "og:image:alt", "og:site_name", "twitter:card",
                    "twitter:title", "twitter:description", "twitter:image"]:
            with self.subTest(key=key):
                self.assertTrue(self.meta(key).strip())
        for key in ["og:image", "twitter:image"]:
            self.assertTrue(local_path(self.meta(key)).is_file(), self.meta(key))

    def test_json_ld(self):
        blocks = [text for attrs, text in self.page.scripts if attrs.get("type") == "application/ld+json"]
        self.assertEqual(len(blocks), 1)
        graph = json.loads(blocks[0])["@graph"]
        person = next(n for n in graph if n["@type"] == "Person")
        self.assertTrue(any(n["@type"] == "WebSite" for n in graph))
        for key in ["name", "url", "image", "jobTitle", "description", "email", "sameAs", "knowsAbout"]:
            self.assertTrue(person.get(key), key)
        self.assertTrue(local_path(person["image"]).is_file(), person["image"])


class TestImages(unittest.TestCase):
    def test_avatar_is_small(self):
        for name in ["aw-200.webp", "aw-200.jpg"]:
            self.assertLess((ROOT / name).stat().st_size, 20_000, name)


class TestMachineReadableFiles(unittest.TestCase):
    links = external_links(parse("index.html"))

    def test_markdown_version_has_every_link(self):
        text = (ROOT / "index.md").read_text(encoding="utf-8")
        for url in self.links:
            self.assertIn(f"({url})", text, f"index.md is missing {url}")

    def test_markdown_version_has_no_front_matter(self):
        # Front matter would make Jekyll render index.md to HTML over index.html.
        self.assertFalse((ROOT / "index.md").read_text(encoding="utf-8").startswith("---"))

    def test_auth_md(self):
        text = (ROOT / "auth.md").read_text(encoding="utf-8")
        # An H1 containing "auth.md"; no front matter, or Jekyll would render it.
        self.assertRegex(text.splitlines()[0], r"^# .*auth\.md")

    def test_llms_txt_has_every_link(self):
        text = (ROOT / "llms.txt").read_text(encoding="utf-8")
        for url in self.links:
            self.assertIn(url, text, f"llms.txt is missing {url}")
        self.assertIn(f"[Home]({SITE})", text)

    def test_robots_txt(self):
        text = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {SITE}sitemap.xml", text)
        self.assertRegex(text, r"(?m)^Content-Signal: .*ai-train=(yes|no)")

    def test_api_catalog(self):
        # RFC 9727: an application/linkset+json document; the Content-Type
        # comes from a Cloudflare response header rule.
        catalog = json.loads((ROOT / ".well-known" / "api-catalog").read_text(encoding="utf-8"))
        self.assertIsInstance(catalog["linkset"], list)

    def test_jekyll_publishes_well_known(self):
        # Jekyll skips dot-directories unless _config.yml includes them.
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        self.assertRegex(config, r"(?m)^include:\n(\s+- .*\n)*\s+- \.well-known$")

    def test_analytics_tracks_sections_and_links(self):
        js = (ROOT / "analytics.js").read_text(encoding="utf-8")
        self.assertIn("'section_toggle'", js)
        self.assertIn("'link_click'", js)
        # The selectors the listeners rely on must still exist in the page.
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('<details class="link-group">', html)
        self.assertIn('class="link-list"', html)

    def test_sitemap(self):
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [e.text for e in ET.parse(ROOT / "sitemap.xml").getroot().findall("s:url/s:loc", ns)]
        self.assertIn(SITE, locs)
        for loc in locs:
            self.assertTrue(local_path(loc).is_file(), loc)


if __name__ == "__main__":
    unittest.main()
