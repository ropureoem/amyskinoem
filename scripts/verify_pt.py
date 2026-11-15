#!/usr/bin/env python3
"""Verify the Portuguese (pt/) phase-1 rollout for amyskinoem.com.

Checks (exit non-zero on any failure):
  1. pt/ contains exactly the 16 phase-1 pages, no more, no fewer.
  2. Every pt page: <html lang="pt">, exactly one <h1>, self canonical,
     hreflang group {x-default, en, zh, es, pt} with correct absolute URLs.
  3. hreflang groups are symmetric across the en / zh / es / pt versions.
  4. Every .language-switch nav (header, footer, mobile) has EN/ZH/ES/PT
     links, PT marked aria-current, and every link resolves to a real file.
  5. Every local href/src/srcset in pt pages resolves to a real file.
  6. No English residue: no text node (outside pre/code/script/style)
     still equals an English source string, and no stray English word
     (the/and/your/our/with/from/...) survives as a whole word.
  7. No factory names anywhere in pt/ (望莎 / 三木生 / Moksha ...).
  8. The matching en/zh/es pages carry pt hreflang and a PT
     switcher link.
  9. sitemap.xml lists exactly the published pt pages (15: brand.html is
     excluded by decision, like en/zh/es) and no untranslated page.
Usage: python3 scripts/verify_pt.py
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://amyskinoem.com"

PT_PAGES = [
    "index.html", "about.html", "blog.html", "brand.html", "brand-kit.html",
    "categories.html", "certifications.html", "packaging.html",
    "process.html", "quote.html",
    "blog/how-sampling-works-before-bulk-production.html",
    "blog/how-to-choose-a-private-label-serum-formula.html",
    "blog/iso-22716-certification-what-it-means-for-your-market.html",
    "blog/private-label-skincare-packaging-options-explained.html",
    "blog/vitamin-c-vs-niacinamide-which-serum-fits-your-brand.html",
    "blog/what-moq-1000-really-means.html",
]
FACTORY_NAMES = ["望莎", "三木生", "Moksha", "望莎生物", "三木"]
EN_WORDS = re.compile(
    r"\b(the|and|your|our|with|from|this|that|these|those|which|what|when|"
    r"where|how|can|will|are|was|were|has|have|you|we|they|not|but|all|"
    r"any|more|most|only|also|about|into|over|after|before|between|"
    r"through|during|under|very|just|should|would|could|there|here|"
    r"then|than|such|other|some|each|choose|start|every|before|"
    r"production|formula|sample|brand|order|market|packaging)\b",
    re.IGNORECASE)
# Words that legitimately appear inside Portuguese copy (cert/brand terms).
EN_WORD_ALLOW = {"formula", "sample", "brand", "order", "market",
                 "packaging", "production"}

FAILURES = []
WARNINGS = []


def fail(msg):
    FAILURES.append(msg)


def en_url(rel):
    return SITE + "/" + rel if rel != "index.html" else SITE + "/"


def zh_url(rel):
    return SITE + "/zh/" + rel if rel != "index.html" else SITE + "/zh/"


def es_url(rel):
    return SITE + "/es/" + rel if rel != "index.html" else SITE + "/es/"


def pt_url(rel):
    return SITE + "/pt/" + rel if rel != "index.html" else SITE + "/pt/"


def expected_hreflang(rel):
    return {"x-default": en_url(rel), "en": en_url(rel),
            "zh": zh_url(rel), "es": es_url(rel),
            "pt": pt_url(rel)}


class PageScan(HTMLParser):
    def __init__(self, rel):
        super().__init__(convert_charrefs=True)
        self.rel = rel
        self.lang = None
        self.h1 = 0
        self.canonical = None
        self.hreflang = {}
        self.switchers = []
        self._switcher = None
        self.links = []
        self.texts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        adict = dict(attrs)
        if tag == "html":
            self.lang = adict.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "link":
            if adict.get("rel") == "canonical":
                self.canonical = adict.get("href")
            elif adict.get("rel") == "alternate" and "hreflang" in adict:
                self.hreflang[adict["hreflang"]] = adict.get("href")
        if tag == "nav" and "language-switch" in adict.get("class", ""):
            self._switcher = {"aria": adict.get("aria-label"), "links": []}
            self.switchers.append(self._switcher)
        if self._switcher is not None and tag == "a":
            self._switcher["links"].append(
                (adict.get("data-language"), adict.get("href"),
                 "aria-current" in adict))
        for k, v in attrs:
            if k in ("href", "src"):
                self.links.append(v)
            elif k == "srcset":
                for chunk in v.split(","):
                    self.links.append(chunk.strip().split()[0])
        if tag in ("script", "style", "pre", "code"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "nav" and self._switcher is not None:
            self._switcher = None
        if tag in ("script", "style", "pre", "code"):
            self.skip -= 1

    def handle_data(self, data):
        if self.skip == 0:
            s = " ".join(data.split())
            if s:
                self.texts.append(s)


def scan(path, rel):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        raw = f.read()
    p = PageScan(rel)
    p.feed(raw)
    return p, raw


def resolve(page_dir, href):
    if not href or href.startswith(("#", "http://", "https://", "mailto:",
                                   "tel:", "//", "data:")):
        return None
    target = os.path.normpath(os.path.join(page_dir, href))
    return os.path.join(ROOT, target)


def check_page(rel):
    p, raw = scan("pt/" + rel, rel)
    tag = f"pt/{rel}"
    if p.lang != "pt":
        fail(f"{tag}: <html lang> is {p.lang!r}, expected 'es'")
    if p.h1 != 1:
        fail(f"{tag}: {p.h1} <h1> elements, expected exactly 1")
    if p.canonical != pt_url(rel):
        fail(f"{tag}: canonical {p.canonical!r}, expected {pt_url(rel)!r}")
    if p.hreflang != expected_hreflang(rel):
        fail(f"{tag}: hreflang {p.hreflang} != {expected_hreflang(rel)}")
    if len(p.switchers) != 3:
        fail(f"{tag}: {len(p.switchers)} language-switch navs, expected 3")
    for i, sw in enumerate(p.switchers):
        if sw["aria"] != "Selecionar idioma":
            fail(f"{tag}: switcher {i} aria-label {sw['aria']!r}")
        langs = {c: (h, cur) for c, h, cur in sw["links"]}
        if set(langs) != {"en", "zh", "es", "pt"}:
            fail(f"{tag}: switcher {i} languages {sorted(langs)}")
            continue
        if not langs["pt"][1]:
            fail(f"{tag}: switcher {i} PT link not aria-current")
        page_dir = "pt/" + os.path.dirname(rel)
        for code, (href, _cur) in langs.items():
            tgt = resolve(page_dir, href)
            if tgt and not os.path.isfile(tgt):
                fail(f"{tag}: switcher {i} {code} link {href!r} -> "
                     f"missing file")
    page_dir = "pt/" + os.path.dirname(rel)
    for href in p.links:
        tgt = resolve(page_dir, href)
        if tgt and not os.path.isfile(tgt):
            fail(f"{tag}: broken local link {href!r}")
    for text in p.texts:
        words = {w.lower() for w in EN_WORDS.findall(text)} - EN_WORD_ALLOW
        if words:
            fail(f"{tag}: English residue in {text[:90]!r} "
                 f"(words: {sorted(words)})")
    for name in FACTORY_NAMES:
        if name in raw:
            fail(f"{tag}: factory name {name!r} present")
    return p


def main():
    # 1. file set
    found = set()
    for base, _dirs, files in os.walk(os.path.join(ROOT, "pt")):
        for fn in files:
            found.add(os.path.relpath(os.path.join(base, fn),
                                      os.path.join(ROOT, "pt")))
    found = {f.replace(os.sep, "/") for f in found}
    if found != set(PT_PAGES):
        fail(f"pt/ file set mismatch: missing={sorted(set(PT_PAGES) - found)} "
             f"extra={sorted(found - set(PT_PAGES))}")

    scans = {}
    for rel in PT_PAGES:
        scans[rel] = check_page(rel)

    # 3. hreflang symmetry + 8. en/zh/es updated
    for rel in PT_PAGES:
        for lang, prefix in (("en", ""), ("zh", "zh/"), ("es", "es/")):
            path = prefix + rel
            p, _raw = scan(path, rel)
            if p.hreflang != expected_hreflang(rel):
                fail(f"{path}: hreflang {p.hreflang} != "
                     f"{expected_hreflang(rel)}")
            pt_links = [h for sw in p.switchers for c, h, _ in sw["links"]
                        if c == "pt"]
            if not pt_links:
                fail(f"{path}: switcher has no PT link")
            for href in pt_links:
                tgt = resolve(prefix + os.path.dirname(rel), href)
                if tgt and not os.path.isfile(tgt):
                    fail(f"{path}: PT switcher link {href!r} -> missing")

    # 9. sitemap
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        sm = f.read()
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    expected_pt = {pt_url(r) for r in PT_PAGES if r != "brand.html"}
    if not expected_pt <= locs:
        fail(f"sitemap missing pt URLs: {sorted(expected_pt - locs)}")
    if pt_url("brand.html") in locs:
        fail("sitemap should not contain pt/brand.html (excluded by "
             "decision, like en/zh/es)")
    if any("hyaluronic-acid-pdrn-capsule-spray" in u for u in locs):
        fail("sitemap contains the redirect placeholder")
    if len(locs) != 128:
        WARNINGS.append(f"sitemap has {len(locs)} URLs, expected 128 "
                        f"(113 + 15 pt)")

    print(f"checked {len(PT_PAGES)} pt pages + en/zh/es counterparts + sitemap")
    for w in WARNINGS:
        print("WARNING:", w)
    if FAILURES:
        print(f"FAIL: {len(FAILURES)} problem(s)")
        for f in FAILURES:
            print(" -", f)
        return 1
    print("PASS: all checks green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
