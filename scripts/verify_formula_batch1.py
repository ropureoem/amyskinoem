#!/usr/bin/env python3
"""Verify formula batch 1 (17 pages x 10 languages = 170 new pages).

Checks (exit non-zero on any failure):
  1. Each of es/pt/it/ru/ar/fr/id/ja/de/th/formulas/ has the 17 batch-1
     pages (plus the 17 batch-2 pages) inside formulas/.
  2. Every new page: correct <html lang> (ar also dir="rtl", others no
     dir), self canonical, hreflang group {x-default, en, zh, es, pt, it,
     ru, ar, fr, id, ja, de, th} with correct absolute URLs.
  3. hreflang groups are symmetric across the en / zh counterparts.
  4. Every .language-switch nav (3 per page) has all 12 languages, own
     language marked aria-current, every link resolves to a real file;
     the footer switcher sits inside #contact.
  5. Every local href/src/srcset in new pages resolves to a real file.
  6. No untranslated text node: no text node (outside pre/code/script/
     style) still equals an English inventory string; for ar/ja/th also
     no stray English word survives as a whole word.
  7. No factory names anywhere in the new pages (望莎 / 三木生 / Moksha).
  8. en/zh formula pages carry the full 12-language hreflang group and
     switchers.
  9. sitemap.xml lists all 170 new URLs (total 588), no brand.html, no
     redirect placeholder hyaluronic-acid-pdrn-capsule-spray.
Usage: python3 scripts/verify_formula_batch1.py
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://amyskinoem.com"
LANGS = ["es", "pt", "it", "ru", "ar", "fr", "id", "ja", "de", "th"]
FORMULA_BATCH1 = [
    "24k-gold-eye-mask.html",
    "24k-gold-hyaluronic-acid-serum.html",
    "amino-acid-cleanser.html",
    "anti-aging-cream.html",
    "banana-facial-cleanser.html",
    "barrier-repairing-essence.html",
    "blushwood-berry-seed-extract-essence.html",
    "body-lotion.html",
    "bosein-sea-buckthorn-cream.html",
    "carrot-face-serum.html",
    "centella-amino-acid-skin-care-set.html",
    "chamomile-facial-mask.html",
    "cica-oil-to-mask-treatment.html",
    "cocoa-butter-sugar-scrub-strawberry.html",
    "color-changing-lip-oil.html",
    "green-tea-facial-cleanser.html",
    "high-moisturizing-cream.html",
]

FORMULA_BATCH2 = [
    "houttuynia-cleansing-spray.html",
    "hyaluronic-acid-serum.html",
    "hydrating-toner.html",
    "hydrogel-v-face-patch.html",
    "leucocyte-firming-face-mask.html",
    "moisturising-cream.html",
    "peptide-serum.html",
    "pink-collagen-crystal-lip-mask.html",
    "niacinamide-serum.html",
    "purifying-facial-cleanser.html",
    "retinol-eye-cream-stick.html",
    "retinol-under-eye-serum.html",
    "self-tanning-oil.html",
    "shampoo.html",
    "sheet-mask.html",
    "sunscreen-spf50.html",
    "vitamin-c-serum.html",
]
FORMULA_PAGES = ["formulas/" + s for s in FORMULA_BATCH1]
FACTORY_NAMES = ["望莎", "三木生", "Moksha", "望莎生物", "三木"]
EN_WORDS = re.compile(
    r"\b(the|and|your|our|with|from|this|that|these|those|which|what|when|"
    r"where|how|can|are|were|has|have|you|we|they|not|but|"
    r"any|more|most|only|about|into|over|after|before|between|"
    r"through|during|under|very|just|should|would|could|there|here|"
    r"then|than|such|other|some|each|choose|every|before|"
    r"production|formula|sample|brand|order|market|packaging)\b",
    re.IGNORECASE)
EN_WORD_ALLOW = {"formula", "sample", "brand", "order", "market",
                 "packaging", "production"}

FAILURES = []
WARNINGS = []


def fail(msg):
    FAILURES.append(msg)


def lang_url(lang, rel):
    if rel == "index.html":
        return SITE + "/" + lang + "/" if lang != "en" else SITE + "/"
    return SITE + "/" + lang + "/" + rel if lang != "en" else SITE + "/" + rel


def expected_hreflang(rel):
    out = {"x-default": lang_url("en", rel), "en": lang_url("en", rel)}
    for lang in ["zh", "es", "pt", "it", "ru", "ar", "fr", "id", "ja",
                 "de", "th"]:
        out[lang] = lang_url(lang, rel)
    return out


# English inventory strings: a translated page must not contain any of
# these verbatim as a text node.
INV_EN = set()
with open(os.path.join(ROOT, "scripts", "i18n",
                       "formula-body-inventory.tsv"),
          encoding="utf-8") as f:
    f.readline()
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 3:
            INV_EN.add(" ".join(p[2].split()))


# Text nodes that legitimately stay in English: nav/loanword labels
# (identical on the phase-1 pages) and batch-2 product names showing up
# in related-formula links (batch 2 owns those names).
ALLOW_NODES = {"Home", "Format", "Serum", "Shampoo", "Essence",
               "Tube, 60 g", "Tube, 2.4 g", "Tube, 125 ml",
               "Jar, 50 g", "Jar, 150 g", "Jar, 250 ml",
               "Hydrogel V Face Patch"}


class PageScan(HTMLParser):
    def __init__(self, rel):
        super().__init__(convert_charrefs=True)
        self.rel = rel
        self.lang = None
        self.dir = None
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
            self.dir = adict.get("dir")
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


def check_page(lang, rel):
    p, raw = scan(f"{lang}/{rel}", rel)
    tag = f"{lang}/{rel}"
    if p.lang != lang:
        fail(f"{tag}: <html lang> is {p.lang!r}, expected {lang!r}")
    if lang == "ar":
        if p.dir != "rtl":
            fail(f"{tag}: <html dir> is {p.dir!r}, expected 'rtl'")
    elif p.dir is not None:
        fail(f"{tag}: <html dir> is {p.dir!r}, expected none")
    if p.h1 != 1:
        fail(f"{tag}: {p.h1} <h1> elements, expected exactly 1")
    if p.canonical != lang_url(lang, rel):
        fail(f"{tag}: canonical {p.canonical!r}, expected "
             f"{lang_url(lang, rel)!r}")
    if p.hreflang != expected_hreflang(rel):
        fail(f"{tag}: hreflang mismatch: "
             f"missing={sorted(set(expected_hreflang(rel)) - set(p.hreflang))} "
             f"extra={sorted(set(p.hreflang) - set(expected_hreflang(rel)))} "
             f"wrong=" + str({k: v for k, v in p.hreflang.items()
                              if expected_hreflang(rel).get(k) != v}))
    if len(p.switchers) != 3:
        fail(f"{tag}: {len(p.switchers)} language-switch navs, expected 3")
    for i, sw in enumerate(p.switchers):
        langs = {c: (h, cur) for c, h, cur in sw["links"]}
        if set(langs) != {"en", "zh", "es", "pt", "it", "ru", "ar", "fr",
                          "id", "ja", "de", "th"}:
            fail(f"{tag}: switcher {i} languages {sorted(langs)}")
            continue
        if not langs[lang][1]:
            fail(f"{tag}: switcher {i} {lang.upper()} link not aria-current")
        page_dir = f"{lang}/{os.path.dirname(rel)}"
        for code, (href, _cur) in langs.items():
            tgt = resolve(page_dir, href)
            if tgt and not os.path.isfile(tgt):
                fail(f"{tag}: switcher {i} {code} link {href!r} -> "
                     f"missing file")
    # footer switcher must sit inside #contact
    contact_pos = raw.find('id="contact"')
    if contact_pos == -1:
        fail(f"{tag}: no #contact section found")
    else:
        nav_positions = [m.start() for m in
                         re.finditer(r'<nav[^>]*language-switch', raw)]
        if not nav_positions or nav_positions[-1] < contact_pos:
            fail(f"{tag}: footer switcher not inside #contact")
    page_dir = f"{lang}/{os.path.dirname(rel)}"
    for href in p.links:
        tgt = resolve(page_dir, href)
        if tgt and not os.path.isfile(tgt):
            fail(f"{tag}: broken local link {href!r}")
    for text in p.texts:
        if text in INV_EN and text not in ALLOW_NODES and \
                any(c.islower() for c in text):
            fail(f"{tag}: untranslated text node {text[:90]!r}")
        if lang in ("ar", "ja", "th"):
            words = {w.lower() for w in EN_WORDS.findall(text)} - \
                EN_WORD_ALLOW
            if words:
                fail(f"{tag}: English residue in {text[:90]!r} "
                     f"(words: {sorted(words)})")
    for name in FACTORY_NAMES:
        if name in raw:
            fail(f"{tag}: factory name {name!r} present")
    return p


def main():
    # 1. file set per language
    for lang in LANGS:
        found = set(os.listdir(os.path.join(ROOT, lang, "formulas")))
        if found != set(FORMULA_BATCH1 + FORMULA_BATCH2):
            fail(f"{lang}/formulas/ mismatch: "
                 f"missing={sorted(set(FORMULA_BATCH1) - found)} "
                 f"extra={sorted(found - set(FORMULA_BATCH1))}")

    for lang in LANGS:
        for rel in FORMULA_PAGES:
            check_page(lang, rel)

    # 3+8. en/zh counterparts: full hreflang + switchers
    for rel in FORMULA_PAGES:
        for lang, prefix in (("en", ""), ("zh", "zh/")):
            p, _raw = scan(prefix + rel, rel)
            if p.hreflang != expected_hreflang(rel):
                fail(f"{prefix}{rel}: hreflang mismatch: "
                     f"missing={sorted(set(expected_hreflang(rel)) - set(p.hreflang))} "
                     f"extra={sorted(set(p.hreflang) - set(expected_hreflang(rel)))}")
            if len(p.switchers) != 3:
                fail(f"{prefix}{rel}: {len(p.switchers)} switcher navs, "
                     f"expected 3")
            for i, sw in enumerate(p.switchers):
                langs = {c for c, _h, _cur in sw["links"]}
                if langs != {"en", "zh", "es", "pt", "it", "ru", "ar",
                             "fr", "id", "ja", "de", "th"}:
                    fail(f"{prefix}{rel}: switcher {i} languages "
                         f"{sorted(langs)}")

    # 9. sitemap
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        sm = f.read()
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    expected_new = set()
    for lang in LANGS:
        for rel in FORMULA_PAGES:
            expected_new.add(lang_url(lang, rel))
    if not expected_new <= locs:
        fail(f"sitemap missing new formula URLs: "
             f"{sorted(expected_new - locs)[:10]}")
    if any(u.endswith("/brand.html") for u in locs):
        fail("sitemap contains brand.html")
    if any("hyaluronic-acid-pdrn-capsule-spray" in u for u in locs):
        fail("sitemap contains the redirect placeholder")
    if len(locs) != 588:
        fail(f"sitemap has {len(locs)} URLs, expected 588")

    print(f"checked {len(LANGS) * len(FORMULA_PAGES)} new pages + "
          f"en/zh counterparts + sitemap")
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
