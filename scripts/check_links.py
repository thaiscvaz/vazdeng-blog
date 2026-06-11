#!/usr/bin/env python3
"""check_links.py — navigational QA against the live site.

Crawls the sitemap, GETs every page, then checks every internal link
and image referenced by each page. External links get a HEAD check
(best-effort; some hosts block bots — reported as WARN, not FAIL).

Usage: python scripts/check_links.py [--base https://vazdeng.pages.dev]
Exit code 1 if any internal 404/5xx found.
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

UA = {"User-Agent": "vazdeng-qa/1.0 (+https://vazdeng.pages.dev)"}
SM_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class RefExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: set[str] = set()
        self.images: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.add(a["href"])
        if tag == "img" and a.get("src"):
            self.images.add(a["src"])


def sitemap_urls(base: str) -> list[str]:
    urls = []
    idx = requests.get(f"{base}/sitemap.xml", headers=UA, timeout=30)
    idx.raise_for_status()
    root = ET.fromstring(idx.content)
    children = [e.text for e in root.findall(".//sm:loc", SM_NS)]
    for child in children:
        if child.endswith("sitemap.xml"):
            sub = requests.get(child, headers=UA, timeout=30)
            subroot = ET.fromstring(sub.content)
            urls += [e.text for e in subroot.findall(".//sm:loc", SM_NS)]
        else:
            urls.append(child)
    return sorted(set(urls))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://vazdeng.pages.dev")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    host = urlparse(base).netloc

    pages = sitemap_urls(base)
    print(f"sitemap: {len(pages)} paginas")

    failures, warns = [], []
    checked: dict[str, int] = {}

    def status(url: str, method: str = "head") -> int:
        if url in checked:
            return checked[url]
        try:
            fn = requests.head if method == "head" else requests.get
            r = fn(url, headers=UA, timeout=30, allow_redirects=True)
            code = r.status_code
            # alguns hosts respondem 405/403 a HEAD; tenta GET antes de acusar
            if method == "head" and code in (403, 405, 501):
                code = requests.get(url, headers=UA, timeout=30).status_code
        except requests.RequestException:
            code = -1
        checked[url] = code
        return code

    refs_to_check: set[str] = set()
    for page in pages:
        code = status(page, method="get")
        if code != 200:
            failures.append(f"PAGE {code}: {page}")
            continue
        html = requests.get(page, headers=UA, timeout=30).text
        ex = RefExtractor()
        ex.feed(html)
        for ref in ex.links | ex.images:
            if ref.startswith(("mailto:", "#", "javascript:", "data:")):
                continue
            refs_to_check.add(urljoin(page, ref))

    internal = sorted(r for r in refs_to_check if urlparse(r).netloc == host)
    external = sorted(r for r in refs_to_check if urlparse(r).netloc != host)
    print(f"refs: {len(internal)} internas, {len(external)} externas")

    for url in internal:
        code = status(url)
        if code in (301, 302):  # allow_redirects segue; só chega aqui se loop
            warns.append(f"REDIR {code}: {url}")
        elif code != 200:
            failures.append(f"INTERNAL {code}: {url}")

    for url in external:
        code = status(url)
        if code != 200:
            warns.append(f"EXTERNAL {code}: {url}")

    print()
    for f in failures:
        print(f"  [FAIL] {f}")
    for w in warns:
        print(f"  [WARN] {w}")
    print(f"\n{len(failures)} falhas internas | {len(warns)} avisos externos")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
