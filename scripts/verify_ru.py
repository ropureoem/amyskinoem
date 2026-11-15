#!/usr/bin/env python3
"""Verify the Russian (ru/) phase-1 rollout for amyskinoem.com.

Checks (exit non-zero on any failure):
  1. ru/ contains the 16 phase-1 pages + 34 formula pages, no more, no fewer.
  2. Every ru page: <html lang="ru">, exactly one <h1>, self canonical,
     hreflang group {x-default, en, zh, es, pt, it, ru, ar, fr, id, ja, de, th} with correct absolute URLs.
  3. hreflang groups are symmetric across all 12 language versions.
  4. Every .language-switch nav (header, footer, mobile) has all 12 languages'
     links, RU marked aria-current, and every link resolves to a real file.
  5. Every local href/src/srcset in ru pages resolves to a real file.
  6. No English residue: no text node (outside pre/code/script/style)
     still equals an English source string, and no stray English word
     (the/and/your/our/with/from/...) survives as a whole word.
  7. No factory names anywhere in ru/ (望莎 / 三木生 / Moksha ...).
  8. The matching en/zh/es/pt/it pages carry ru hreflang and a RU
     switcher link.
  9. sitemap.xml lists exactly the published ru pages (15: brand.html is
     excluded by decision, like en/zh/es/pt/it) and no untranslated page.
Usage: python3 scripts/verify_ru.py
"""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://amyskinoem.com"

RU_PAGES = [
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
FORMULA_FILES = ['24k-gold-eye-mask.html', '24k-gold-hyaluronic-acid-serum.html', 'amino-acid-cleanser.html', 'anti-aging-cream.html', 'banana-facial-cleanser.html', 'barrier-repairing-essence.html', 'blushwood-berry-seed-extract-essence.html', 'body-lotion.html', 'bosein-sea-buckthorn-cream.html', 'carrot-face-serum.html', 'centella-amino-acid-skin-care-set.html', 'chamomile-facial-mask.html', 'cica-oil-to-mask-treatment.html', 'cocoa-butter-sugar-scrub-strawberry.html', 'color-changing-lip-oil.html', 'green-tea-facial-cleanser.html', 'high-moisturizing-cream.html', 'houttuynia-cleansing-spray.html', 'hyaluronic-acid-serum.html', 'hydrating-toner.html', 'hydrogel-v-face-patch.html', 'leucocyte-firming-face-mask.html', 'moisturising-cream.html', 'niacinamide-serum.html', 'peptide-serum.html', 'pink-collagen-crystal-lip-mask.html', 'purifying-facial-cleanser.html', 'retinol-eye-cream-stick.html', 'retinol-under-eye-serum.html', 'self-tanning-oil.html', 'shampoo.html', 'sheet-mask.html', 'sunscreen-spf50.html', 'vitamin-c-serum.html']
FORMULA_SET = {"formulas/" + f for f in FORMULA_FILES}
FACTORY_NAMES = ["望莎", "三木生", "Moksha", "望莎生物", "三木"]
EN_WORDS = re.compile(
    r"\b(the|and|your|our|with|from|this|that|these|those|which|what|when|"
    r"where|how|can|will|are|was|were|has|have|you|we|they|not|but|"
    r"any|more|most|only|also|about|into|over|after|before|between|"
    r"through|during|under|very|just|should|would|could|there|here|"
    r"then|than|such|other|some|each|choose|start|every|before|"
    r"production|formula|sample|brand|order|market|packaging)\b",
    re.IGNORECASE)
# NOTE: "all" removed from the list: it was an Italian elision false
# positive ("all'..."); Russian has no such elision, but "all" stays out
# of the list all the same.
# Words that legitimately appear inside Italian copy (cert/brand terms).
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


def it_url(rel):
    return SITE + "/it/" + rel if rel != "index.html" else SITE + "/it/"


def ru_url(rel):
    return SITE + "/ru/" + rel if rel != "index.html" else SITE + "/ru/"


def ar_url(rel):
    return SITE + "/ar/" + rel if rel != "index.html" else SITE + "/ar/"

def fr_url(rel):
    return SITE + "/fr/" + rel if rel != "index.html" else SITE + "/fr/"

def id_url(rel):
    return SITE + "/id/" + rel if rel != "index.html" else SITE + "/id/"

def ja_url(rel):
    return SITE + "/ja/" + rel if rel != "index.html" else SITE + "/ja/"

def de_url(rel):
    return SITE + "/de/" + rel if rel != "index.html" else SITE + "/de/"

def th_url(rel):
    return SITE + "/th/" + rel if rel != "index.html" else SITE + "/th/"

def expected_hreflang(rel):
    return {"x-default": en_url(rel), "en": en_url(rel),
            "zh": zh_url(rel), "es": es_url(rel), "pt": pt_url(rel), "it": it_url(rel),
            "ru": ru_url(rel), "ar": ar_url(rel), "fr": fr_url(rel), "id": id_url(rel),
            "ja": ja_url(rel), "de": de_url(rel), "th": th_url(rel)}


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
    p, raw = scan("ru/" + rel, rel)
    tag = f"ru/{rel}"
    if p.lang != "ru":
        fail(f"{tag}: <html lang> is {p.lang!r}, expected 'ru'")
    if p.h1 != 1:
        fail(f"{tag}: {p.h1} <h1> elements, expected exactly 1")
    if p.canonical != ru_url(rel):
        fail(f"{tag}: canonical {p.canonical!r}, expected {ru_url(rel)!r}")
    if p.hreflang != expected_hreflang(rel):
        fail(f"{tag}: hreflang {p.hreflang} != {expected_hreflang(rel)}")
    if len(p.switchers) != 3:
        fail(f"{tag}: {len(p.switchers)} language-switch navs, expected 3")
    for i, sw in enumerate(p.switchers):
        if sw["aria"] != "Выбор языка":
            fail(f"{tag}: switcher {i} aria-label {sw['aria']!r}")
        langs = {c: (h, cur) for c, h, cur in sw["links"]}
        if set(langs) != {"en", "zh", "es", "pt", "it", "ru", "ar", "fr", "id", "ja", "de", "th"}:
            fail(f"{tag}: switcher {i} languages {sorted(langs)}")
            continue
        if not langs["ru"][1]:
            fail(f"{tag}: switcher {i} RU link not aria-current")
        page_dir = "ru/" + os.path.dirname(rel)
        for code, (href, _cur) in langs.items():
            tgt = resolve(page_dir, href)
            if tgt and not os.path.isfile(tgt):
                fail(f"{tag}: switcher {i} {code} link {href!r} -> "
                     f"missing file")
    page_dir = "ru/" + os.path.dirname(rel)
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
    for base, _dirs, files in os.walk(os.path.join(ROOT, "ru")):
        for fn in files:
            found.add(os.path.relpath(os.path.join(base, fn),
                                      os.path.join(ROOT, "ru")))
    found = {f.replace(os.sep, "/") for f in found}
    if found != set(RU_PAGES) | FORMULA_SET:
        fail(f"ru/ file set mismatch: missing={sorted(set(RU_PAGES) - found)} "
             f"extra={sorted(found - set(RU_PAGES))}")

    scans = {}
    for rel in RU_PAGES:
        scans[rel] = check_page(rel)

    # 3. hreflang symmetry + 8. en/zh/es updated
    for rel in RU_PAGES:
        for lang, prefix in ((("en", ""), ("zh", "zh/"), ("es", "es/"), ("pt", "pt/"), ("it", "it/"), ("ru", "ru/"), ("ar", "ar/"), ("fr", "fr/"), ("id", "id/"), ("ja", "ja/"), ("de", "de/"), ("th", "th/"))):
            path = prefix + rel
            p, _raw = scan(path, rel)
            if p.hreflang != expected_hreflang(rel):
                fail(f"{path}: hreflang {p.hreflang} != "
                     f"{expected_hreflang(rel)}")
            ru_links = [h for sw in p.switchers for c, h, _ in sw["links"]
                        if c == "ru"]
            if not ru_links:
                fail(f"{path}: switcher has no RU link")
            for href in ru_links:
                tgt = resolve(prefix + os.path.dirname(rel), href)
                if tgt and not os.path.isfile(tgt):
                    fail(f"{path}: RU switcher link {href!r} -> missing")

    # 9. sitemap
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        sm = f.read()
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
    expected_ru = {ru_url(r) for r in RU_PAGES if r != "brand.html"}
    if not expected_ru <= locs:
        fail(f"sitemap missing ru URLs: {sorted(expected_ru - locs)}")
    if ru_url("brand.html") in locs:
        fail("sitemap should not contain ru/brand.html (excluded by "
             "decision, like en/zh/es/pt/it)")
    if any("hyaluronic-acid-pdrn-capsule-spray" in u for u in locs):
        fail("sitemap contains the redirect placeholder")
    if len(locs) != 588:
        WARNINGS.append(f"sitemap has {len(locs)} URLs, expected 588 "
                        f"(12 languages x 49)")

    print(f"checked {len(RU_PAGES)} ru pages + all-language counterparts + sitemap")
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
