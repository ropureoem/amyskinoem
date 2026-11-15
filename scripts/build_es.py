#!/usr/bin/env python3
"""Build Spanish (es/) pages for amyskinoem.com from the English originals.

Usage: python3 scripts/build_es.py [--update-en-zh]

- Copies the 16 phase-1 English pages into es/ (same filenames).
- Rewrites relative paths by depth (../ for root pages, ../../ for blog/).
- Translates text nodes and translatable attributes with scripts/i18n/es.tsv
  (exact match first, then longest-first phrase replacement inside a string).
- <pre>/<code>/<style> and non-JSON-LD <script> are copied verbatim.
- Links to formulas/ point at the English formulas/ until phase 2 (no es
  formula pages exist yet); they are flipped back when phase 2 lands.
- Rebuilds hreflang (x-default -> en, en, zh, es, pt) and the .language-switch
  navs (EN/ZH/ES/PT, aria-label "Selección de idioma").
- With --update-en-zh, also adds x-default + es hreflang and an ES switcher
  link to the matching en/ and zh/ pages (only for pages that have an es
  version). Never touches any other page, and never touches English content.
- Writes a coverage report to /tmp/eswork/build-report.json.
"""
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://amyskinoem.com"
TODAY = "2026-11-15"

ES_PAGES = [
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

VOID = {"meta", "link", "img", "br", "hr", "input", "area", "base", "col",
        "embed", "source", "track", "wbr"}
TRANSLATE_ATTRS = {"alt", "aria-label", "placeholder", "title"}
SKIP_JSONLD_KEYS = {"url", "logo", "email", "@type", "@context", "image",
                    "contactType"}


def load_glossary():
    path = os.path.join(ROOT, "scripts", "i18n", "es.tsv")
    glossary = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            if "\t" not in line:
                continue
            en, es = line.split("\t", 1)
            en, es = en.strip(), es.strip()
            if en and es and en not in glossary:
                glossary[en] = es
    return glossary


GLOSSARY = load_glossary()
PHRASES = sorted(GLOSSARY, key=len, reverse=True)

REPORT = {"exact": 0, "phrase": [], "untranslated": [], "pages": {}}


def norm(s):
    return " ".join(s.split())


def translate_text(s):
    """Return (translated, method). method: exact|phrase|same."""
    stripped = norm(s)
    if not stripped:
        return s, "same"
    if stripped in GLOSSARY:
        REPORT["exact"] += 1
        return _rewrap(s, GLOSSARY[stripped]), "exact"
    out = stripped
    for phrase in PHRASES:
        if phrase in out:
            # word-boundary guard: never replace inside another word
            # (e.g. bare "and" must not touch "Ashland").
            out = re.sub(r"(?<![A-Za-z])" + re.escape(phrase) + r"(?![A-Za-z])",
                         GLOSSARY[phrase], out)
    if out != stripped:
        REPORT["phrase"].append((stripped, out))
        return _rewrap(s, out), "phrase"
    return s, "same"


def _rewrap(orig, new):
    lead = orig[: len(orig) - len(orig.lstrip())]
    trail = orig[len(orig.rstrip()):]
    return lead + new + trail


def es_url(rel):
    if rel == "index.html":
        return SITE + "/es/"
    return SITE + "/es/" + rel


def en_url(rel):
    if rel == "index.html":
        return SITE + "/"
    return SITE + "/" + rel


def zh_url(rel):
    if rel == "index.html":
        return SITE + "/zh/"
    return SITE + "/zh/" + rel


def pt_url(rel):
    if rel == "index.html":
        return SITE + "/pt/"
    return SITE + "/pt/" + rel


def relpath(from_dir, target):
    """Relative URL from directory `from_dir` (site-relative, '' = site
    root) to site-relative `target`."""
    return os.path.relpath(target, from_dir or ".").replace(os.sep, "/")


def switcher_html(rel, current="es"):
    """Language-switcher inner anchors for the es page `rel`."""
    es_dir = "es" if not os.path.dirname(rel) else "es/" + os.path.dirname(rel)
    links = []
    for code, target, label in (
        ("en", rel, "EN"),
        ("zh", "zh/" + rel, "ZH"),
        ("es", "es/" + rel, "ES"),
        ("pt", "pt/" + rel, "PT"),
    ):
        href = relpath(es_dir, target)
        cur = ' aria-current="true"' if code == current else ""
        links.append(
            f'<a{cur} data-language="{code}" href="{href}" '
            f'hreflang="{code}" lang="{code}">{label}</a>'
        )
    return "".join(links)


class EsBuilder(HTMLParser):
    def __init__(self, rel):
        super().__init__(convert_charrefs=True)
        self.rel = rel
        self.dir = os.path.dirname(rel)          # en-side dir (for resolving)
        self.es_dir = "es" if not self.dir else "es/" + self.dir
        self.out = []
        self.skip = 0          # inside script/style/pre/code
        self.in_jsonld = False
        self.jsonld_buf = []
        self.in_switcher = False
        self.hreflang_done = False

    # -- structural helpers -------------------------------------------------
    def rewrite_href(self, value):
        if not value or value.startswith(("#", "http://", "https://",
                                          "mailto:", "tel:", "//", "data:")):
            return value
        target = os.path.normpath(os.path.join(self.dir, value))
        target = target.replace(os.sep, "/")
        if target in ES_PAGES:
            return relpath(self.es_dir, "es/" + target)
        if target.startswith("formulas/"):
            # No es formula pages yet (phase 2): link to the English page.
            return relpath(self.es_dir, target)
        return relpath(self.es_dir, target)

    def rewrite_srcset(self, value):
        parts = []
        for chunk in value.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            bits = chunk.split()
            bits[0] = self.rewrite_href(bits[0])
            parts.append(" ".join(bits))
        return ", ".join(parts)

    def emit_tag(self, tag, attrs, selfclose=False):
        out_attrs = []
        for k, v in attrs:
            if v is None:
                out_attrs.append(k)
                continue
            if tag == "html" and k == "lang":
                v = "es"
            elif k in ("href", "src") and tag not in ("link",):
                v = self.rewrite_href(v)
            elif k in ("href", "src") and tag == "link":
                v = self.rewrite_href(v)
            elif k == "srcset":
                v = self.rewrite_srcset(v)
            elif k in TRANSLATE_ATTRS:
                v, _ = translate_text(v)
            elif tag == "meta" and k == "content":
                name = dict(attrs).get("name") or dict(attrs).get("property") or ""
                if name in ("description", "keywords", "og:title",
                            "og:description"):
                    v, _ = translate_text(v)
                elif name == "og:url":
                    v = es_url(self.rel)
            elif tag == "link" and k == "href":
                pass
            out_attrs.append(f'{k}="{html.escape(v, quote=True)}"')
        close = "/>" if selfclose else ">"
        self.out.append(f"<{tag}" + (" " if out_attrs else "") +
                        " ".join(out_attrs) + close)

    # -- parser callbacks ---------------------------------------------------
    def handle_decl(self, decl):
        self.out.append(f"<!{decl}>")

    def handle_comment(self, data):
        if self.skip == 0:
            self.out.append(f"<!--{data}-->")

    def handle_starttag(self, tag, attrs):
        adict = dict(attrs)
        if tag == "link" and "hreflang" in adict:
            return  # dropped; rebuilt after canonical
        if tag == "link" and adict.get("rel") == "canonical":
            attrs = [(k, es_url(self.rel) if k == "href" else v)
                     for k, v in attrs]
            self.emit_tag(tag, attrs)
            if not self.hreflang_done:
                self.hreflang_done = True
                for code, url in (("x-default", en_url(self.rel)),
                                  ("en", en_url(self.rel)),
                                  ("zh", zh_url(self.rel)),
                                  ("es", es_url(self.rel)),
                                  ("pt", pt_url(self.rel))):
                    self.out.append(
                        f'<link href="{url}" hreflang="{code}" '
                        f'rel="alternate"/>')
            return
        if tag == "nav" and "language-switch" in adict.get("class", ""):
            new_attrs = []
            for k, v in attrs:
                if k == "aria-label":
                    v = "Selección de idioma"
                new_attrs.append((k, v))
            self.emit_tag(tag, new_attrs)
            self.out.append(switcher_html(self.rel))
            self.in_switcher = True
            return
        if self.in_switcher:
            return
        if tag in ("script", "style", "pre", "code"):
            self.skip += 1
            if tag == "script" and adict.get("type") == "application/ld+json":
                self.in_jsonld = True
                self.jsonld_buf = []
                self.out.append(self._open_tag(tag, attrs))
                return
        self.emit_tag(tag, attrs)

    def _open_tag(self, tag, attrs):
        parts = []
        for k, v in attrs:
            parts.append(k if v is None else
                         f'{k}="{html.escape(v, quote=True)}"')
        return "<" + tag + (" " if parts else "") + " ".join(parts) + ">"

    def handle_startendtag(self, tag, attrs):
        if self.in_switcher:
            return
        adict = dict(attrs)
        if tag == "link" and "hreflang" in adict:
            return
        if tag == "link" and adict.get("rel") == "canonical":
            attrs = [(k, es_url(self.rel) if k == "href" else v)
                     for k, v in attrs]
            self.emit_tag(tag, attrs, selfclose=True)
            if not self.hreflang_done:
                self.hreflang_done = True
                for code, url in (("x-default", en_url(self.rel)),
                                  ("en", en_url(self.rel)),
                                  ("zh", zh_url(self.rel)),
                                  ("es", es_url(self.rel)),
                                  ("pt", pt_url(self.rel))):
                    self.out.append(
                        f'<link href="{url}" hreflang="{code}" '
                        f'rel="alternate"/>')
            return
        self.emit_tag(tag, attrs, selfclose=True)

    def handle_endtag(self, tag):
        if tag == "head" and not self.hreflang_done:
            # Page had no canonical (e.g. brand.html): insert canonical +
            # hreflang group just before </head> so the es page is complete.
            self.out.append(
                f'<link rel="canonical" href="{es_url(self.rel)}">')
            for code, url in (("x-default", en_url(self.rel)),
                              ("en", en_url(self.rel)),
                              ("zh", zh_url(self.rel)),
                              ("es", es_url(self.rel)),
                              ("pt", pt_url(self.rel))):
                self.out.append(
                    f'<link href="{url}" hreflang="{code}" '
                    f'rel="alternate"/>')
            self.hreflang_done = True
        if tag == "nav" and self.in_switcher:
            self.out.append("</nav>")
            self.in_switcher = False
            return
        if self.in_switcher:
            return
        if self.in_jsonld and tag == "script":
            raw = "".join(self.jsonld_buf)
            self.out.append(translate_jsonld(raw))
            self.out.append("</script>")
            self.in_jsonld = False
            self.skip -= 1
            return
        if tag in ("script", "style", "pre", "code"):
            self.skip -= 1
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld_buf.append(data)
            return
        if self.in_switcher:
            return  # switcher inner content replaced wholesale
        if self.skip > 0:
            self.out.append(data)
            return
        stripped = norm(data)
        if not stripped:
            self.out.append(data)
            return
        new, method = translate_text(data)
        if method == "same" and re.search(r"[A-Za-z]", stripped):
            REPORT["untranslated"].append((self.rel, stripped))
        self.out.append(html.escape(new, quote=False) if method != "same"
                        else data)


def translate_jsonld(raw):
    try:
        data = json.loads(raw)
    except Exception:
        return raw

    def walk(o, key=None):
        if isinstance(o, dict):
            return {k: walk(v, k) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v, key) for v in o]
        if isinstance(o, str):
            if key in SKIP_JSONLD_KEYS or "http" in o or "@" in o:
                return o
            new, method = translate_text(o)
            if method == "same" and re.search(r"[A-Za-z]{3,}", o):
                REPORT["untranslated"].append(("jsonld", o))
            return new
        return o

    return json.dumps(walk(data), ensure_ascii=False, separators=(",", ":"))


def build_es_page(rel):
    src = os.path.join(ROOT, rel)
    with open(src, encoding="utf-8") as f:
        raw = f.read()
    builder = EsBuilder(rel)
    builder.feed(raw)
    builder.close()
    dest = os.path.join(ROOT, "es", rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write("".join(builder.out))
    return dest


def es_href_for_page(base_rel, lang):
    """Relative href from the en/zh page `base_rel` to its es counterpart."""
    if lang == "en":
        base_dir = os.path.dirname(base_rel)
        return relpath(base_dir, "es/" + base_rel)
    zh_dir = "zh" if not os.path.dirname(base_rel) else \
        "zh/" + os.path.dirname(base_rel)
    return relpath(zh_dir, "es/" + base_rel)


def update_en_zh(rel):
    """Add x-default + es hreflang and an ES switcher link to en/zh pages."""
    en = en_url(rel)
    zh = zh_url(rel)
    es = es_url(rel)
    for lang in ("en", "zh"):
        path = rel if lang == "en" else "zh/" + rel
        full = os.path.join(ROOT, path)
        with open(full, encoding="utf-8") as f:
            raw = f.read()
        orig = raw
        if f'hreflang="es"' in raw:
            print(f"skip {path}: es hreflang already present")
            continue
        old_en = (f'<link href="{en}" hreflang="en" rel="alternate"/>')
        new_en = (f'<link href="{en}" hreflang="x-default" '
                  f'rel="alternate"/><link href="{en}" hreflang="en" '
                  f'rel="alternate"/>')
        assert old_en in raw, f"hreflang en not found in {path}"
        raw = raw.replace(old_en, new_en, 1)
        old_zh = (f'<link href="{zh}" hreflang="zh" rel="alternate"/>')
        new_zh = (old_zh + f'<link href="{es}" hreflang="es" '
                  f'rel="alternate"/>')
        assert old_zh in raw, f"hreflang zh not found in {path}"
        raw = raw.replace(old_zh, new_zh, 1)
        # switcher: insert ES anchor after the ZH anchor (all occurrences)
        es_href = es_href_for_page(rel, lang)
        zh_anchor = re.compile(
            r'(<a(?: aria-current="true")? data-language="zh" href="[^"]+" '
            r'hreflang="zh" lang="zh">ZH</a>)')
        assert zh_anchor.search(raw), f"ZH switcher anchor not in {path}"
        es_anchor = (f'<a data-language="es" href="{es_href}" '
                     f'hreflang="es" lang="es">ES</a>')
        raw, n = zh_anchor.subn(r"\1" + es_anchor, raw)
        assert n in (2, 3), f"unexpected switcher count {n} in {path}"
        if raw != orig:
            with open(full, "w", encoding="utf-8") as f:
                f.write(raw)
        print(f"updated {path}: hreflang +es, switcher +ES ({n} navs)")


def main():
    update = "--update-en-zh" in sys.argv
    for rel in ES_PAGES:
        dest = build_es_page(rel)
        print("built", dest)
    if update:
        for rel in ES_PAGES:
            update_en_zh(rel)
    with open("/tmp/eswork/build-report.json", "w", encoding="utf-8") as f:
        json.dump(REPORT, f, ensure_ascii=False, indent=1)
    print(f"exact={REPORT['exact']} phrase_changes="
          f"{len(REPORT['phrase'])} untranslated="
          f"{len(REPORT['untranslated'])}")


if __name__ == "__main__":
    main()
