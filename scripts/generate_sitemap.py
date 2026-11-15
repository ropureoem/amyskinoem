#!/usr/bin/env python3
"""Regenerate sitemap.xml for amyskinoem.com from the actual files on disk.

- Scans en / zh / es / pt / it / ru page sets (root pages + blog/ + formulas/).
- Excludes: brand.html (not in the sitemap by decision, all languages),
  the meta-refresh redirect placeholder
  formulas/hyaluronic-acid-pdrn-capsule-spray.html, and 404.html.
- Format follows the site's existing one: <loc> + <lastmod> +
  <changefreq>weekly</changefreq> + <priority>.
  Priority mirrors the English page: index 1.0, categories 0.9,
  formulas 0.8, everything else 0.7.
- Preserves the recorded <lastmod>/<priority> of URLs already in the
  sitemap; new URLs get lastmod = today (override with --date YYYY-MM-DD).
- Never submits anything to GSC; new-language URLs only enter the sitemap
  for natural discovery (English first, per the 2026-11-15 decision).
- Prints a summary and exits non-zero if the URL count changed
  unexpectedly (use --force to write anyway).
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://amyskinoem.com"
TODAY = "2026-11-15"

ROOT_PAGES = ["index.html", "about.html", "blog.html", "brand-kit.html",
              "categories.html", "certifications.html", "packaging.html",
              "process.html", "quote.html"]
EXCLUDE_FILES = {"brand.html",
                 "formulas/hyaluronic-acid-pdrn-capsule-spray.html",
                 "404.html"}
LANGS = ["en", "zh", "es", "pt", "it", "ru", "ar", "fr"]


def pages_for_lang(lang):
    """Site-relative page paths that exist for `lang` ('en' = root)."""
    base = "" if lang == "en" else lang
    out = []
    for rel in ROOT_PAGES:
        p = os.path.join(base, rel) if base else rel
        if os.path.isfile(os.path.join(ROOT, p)):
            out.append(rel)
    for sub in ("blog", "formulas"):
        d = os.path.join(ROOT, base, sub) if base else os.path.join(ROOT, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".html"):
                continue
            rel = f"{sub}/{fn}"
            if rel in EXCLUDE_FILES:
                continue
            out.append(rel)
    return out


def url_for(lang, rel):
    if lang == "en":
        return SITE + "/" + rel if rel != "index.html" else SITE + "/"
    if rel == "index.html":
        return f"{SITE}/{lang}/"
    return f"{SITE}/{lang}/{rel}"


def priority_for(rel):
    if rel == "index.html":
        return "1.0"
    if rel == "categories.html":
        return "0.9"
    if rel.startswith("formulas/"):
        return "0.8"
    return "0.7"


def read_existing():
    path = os.path.join(ROOT, "sitemap.xml")
    existing = {}
    if not os.path.isfile(path):
        return existing
    tree = ET.parse(path)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for url in tree.getroot().findall("s:url", ns):
        loc = url.findtext("s:loc", namespaces=ns)
        lastmod = url.findtext("s:lastmod", namespaces=ns)
        prio = url.findtext("s:priority", namespaces=ns)
        if loc:
            existing[loc] = (lastmod, prio)
    return existing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=TODAY)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    existing = read_existing()
    urls = []  # (loc, lastmod, priority)
    for lang in LANGS:
        for rel in pages_for_lang(lang):
            loc = url_for(lang, rel)
            if loc in existing:
                lastmod, prio = existing[loc]
            else:
                lastmod, prio = args.date, priority_for(rel)
            urls.append((loc, lastmod, prio))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, prio in urls:
        lines.append(
            f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>"
            f"<changefreq>weekly</changefreq><priority>{prio}</priority></url>")
    lines.append("</urlset>")
    new = [u for u in urls if u[0] not in existing]
    dropped = [u for u in existing if u not in {x[0] for x in urls}]
    print(f"total={len(urls)} en={sum(1 for u in urls if '/zh/' not in u[0] and '/es/' not in u[0] and '/pt/' not in u[0] and '/it/' not in u[0] and '/ru/' not in u[0])} "
          f"zh={sum(1 for u in urls if '/zh/' in u[0])} "
          f"es={sum(1 for u in urls if '/es/' in u[0])} "
          f"pt={sum(1 for u in urls if '/pt/' in u[0])} "
          f"it={sum(1 for u in urls if '/it/' in u[0])} "
          f"ru={sum(1 for u in urls if '/ru/' in u[0])} "
          f"ar={sum(1 for u in urls if '/ar/' in u[0])} "
          f"new={len(new)} dropped={len(dropped)}")
    for loc, _, _ in new:
        print("  +", loc)
    for loc in dropped:
        print("  -", loc)
    if dropped and not args.force:
        print("ERROR: existing URLs would be dropped; refusing to write "
              "(use --force if intentional)", file=sys.stderr)
        return 1
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote sitemap.xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
