#!/usr/bin/env python3
"""Consistency checks for the ClearMetricTools static site.

Every page is a self-contained HTML file, so shared blocks (nav, disclaimer,
translations, export code) are copied by hand and drift easily. This script
catches the drift that is cheap to detect mechanically. It does not check
that any tax number or formula is correct.

Usage:  python check_site.py [site_root]      (default: current directory)
        python check_site.py --live https://clearmetrictools.com [site_root]
Exit code 0 = no problems, 1 = problems found.
"""
import re
import sys
import urllib.request
from pathlib import Path

LANGS = ["en", "fr", "de", "es"]
REQUIRED_FUNCS = ["calc", "getSummaryText", "exportToTxt", "exportToPdf"]
FEEDBACK_HOST = "forms.gle"
# Text pages with no calculator: no calc/export code, linked from the footer
# links on every page instead of the nav.
INFO_PAGES = {"about.html", "privacy.html"}


def pages(root):
    return sorted(p for p in root.rglob("*.html") if ".git" not in p.parts and ".claude" not in p.parts)


def i18n_keys(src):
    """Return {lang: set(keys)} for the page's main i18n object, or None."""
    m = re.search(r"const\s+i18n\s*=\s*\{", src)
    if not m:
        return None
    out = {}
    for lang in LANGS:
        lm = re.search(r"\b%s\s*:\s*\{" % lang, src[m.end():])
        if not lm:
            out[lang] = None
            continue
        start = m.end() + lm.end()
        depth, i, quote = 1, start, None
        while i < len(src) and depth:
            c = src[i]
            if quote:
                if c == "\\":
                    i += 1
                elif c == quote:
                    quote = None
            elif c in "\"'`":
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        body = src[start:i - 1]
        # strip string contents so text like "Scenarios:" is not read as a key
        body = re.sub(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`", '""', body)
        out[lang] = set(re.findall(r"([A-Za-z_]\w*)\s*:", body))
    return out


def check_page(path, root):
    problems = []
    src = path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(root).as_posix()

    # 1. local links must resolve
    for href in re.findall(r"""(?:href|src)\s*=\s*["']([^"'#]+)""", src):
        if re.match(r"(?:[a-z]+:|//)", href, re.I):
            continue
        target = (path.parent / href.split("?")[0]).resolve()
        if not target.exists():
            problems.append("broken local link: %s" % href)

    # 2. nothing loaded from other domains (privacy promise in CLAUDE.md)
    # A canonical link to the site's own domain is a label for search engines,
    # not a download, so it is exempt.
    loaded = re.sub(r"""<link\b[^>]*\brel\s*=\s*["']canonical["'][^>]*href\s*=\s*["']https://clearmetrictools\.com/[^"']*["'][^>]*>""", "", src, flags=re.I)
    for tag, url in re.findall(r"""<(script|link|img|iframe)\b[^>]*?(?:src|href)\s*=\s*["']((?:https?:)?//[^"']+)""", loaded, re.I):
        problems.append("external resource in <%s>: %s" % (tag, url))

    # 3. shared blocks present
    if 'id="tDisclaimer"' not in src:
        problems.append("disclaimer footer (#tDisclaimer) missing")
    if FEEDBACK_HOST not in src:
        problems.append("feedback button link missing")
    for fn in ([] if rel in INFO_PAGES else REQUIRED_FUNCS):
        if not re.search(r"function\s+%s\s*\(" % fn, src):
            problems.append("function %s() missing" % fn)
    if 'class="legal-links"' not in src:
        problems.append("footer links to About and Privacy (.legal-links) missing")
    if not re.search(r"<title>[^<]+</title>", src):
        problems.append("<title> missing or empty")

    # 4. every getElementById('x') must have a matching id="x"
    ids = set(re.findall(r"""\bid\s*=\s*["']([^"']+)""", src))
    for ref in sorted(set(re.findall(r"""getElementById\(\s*['"]([^'"]+)['"]\s*\)""", src))):
        if ref not in ids:
            problems.append("script uses id '%s' but no element has it" % ref)

    # 5. duplicate ids
    all_ids = re.findall(r"""<[a-zA-Z][^>]*?\bid\s*=\s*["']([^"']+)""", src)
    for dup in sorted({x for x in all_ids if all_ids.count(x) > 1}):
        problems.append("id '%s' is used more than once" % dup)

    # 6. translations complete (pages that have an i18n object)
    keys = i18n_keys(src)
    if keys:
        for lang in LANGS:
            if keys[lang] is None:
                problems.append("i18n has no '%s' block" % lang)
        base = keys.get("en") or set()
        for lang in LANGS[1:]:
            if keys.get(lang) is None:
                continue
            missing = sorted(base - keys[lang])
            extra = sorted(keys[lang] - base)
            if missing:
                problems.append("i18n '%s' is missing keys: %s" % (lang, ", ".join(missing)))
            if extra:
                problems.append("i18n '%s' has keys not in 'en': %s" % (lang, ", ".join(extra)))
    return rel, problems


def nav_signature(path):
    src = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'<div class="nav-links">(.*?)</div>', src, re.S)
    if not m:
        return None
    return tuple(re.findall(r'<a\s[^>]*href="([^"]+)"', m.group(1)))


def check_nav(root, all_pages):
    """Pages in the same folder should link to the same set of pages."""
    problems = []
    groups = {}
    for p in all_pages:
        groups.setdefault(p.parent, []).append(p)
    for folder, members in groups.items():
        sigs = {}
        for p in members:
            sigs.setdefault(nav_signature(p), []).append(p.name)
        if len(sigs) > 1:
            label = folder.relative_to(root).as_posix() or "(root)"
            detail = "; ".join("%s -> %s" % (", ".join(v), list(k) if k else "no nav") for k, v in sigs.items())
            problems.append("nav differs between pages in %s: %s" % (label, detail))
        linked = {h for s in sigs if s for h in s if "/" not in h}
        for p in members:
            if p.relative_to(root).as_posix() in INFO_PAGES:
                continue
            if linked and p.name not in linked:
                problems.append("%s is not linked from its own nav" % p.relative_to(root).as_posix())
    return problems


def check_live(base, root, all_pages):
    problems = []
    targets = [p.relative_to(root).as_posix() for p in all_pages]
    for rel in targets:
        url = base.rstrip("/") + "/" + rel
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "site-check"})
            with urllib.request.urlopen(req, timeout=20) as r:
                live = r.read()
            local = (root / rel).read_bytes()
            if live.replace(b"\r\n", b"\n") != local.replace(b"\r\n", b"\n"):
                problems.append("%s: live copy differs from the local file (not deployed yet, or cached)" % rel)
        except Exception as e:  # noqa: BLE001 - report any fetch failure
            problems.append("%s: could not fetch (%s)" % (url, e))
    return problems


def main(argv):
    live = None
    args = list(argv)
    if "--live" in args:
        i = args.index("--live")
        live = args[i + 1]
        del args[i:i + 2]
    root = Path(args[0] if args else ".").resolve()
    all_pages = pages(root)
    if not all_pages:
        print("No .html files under %s" % root)
        return 1
    total = 0
    for p in all_pages:
        rel, problems = check_page(p, root)
        print("%s  %s" % ("OK  " if not problems else "FAIL", rel))
        for x in problems:
            print("      - " + x)
        total += len(problems)
    for x in check_nav(root, all_pages):
        print("FAIL  nav: " + x)
        total += 1
    if live:
        for x in check_live(live, root, all_pages):
            print("FAIL  live: " + x)
            total += 1
    print("\n%d page(s) checked, %d problem(s)." % (len(all_pages), total))
    print("Note: this does not verify any tax rate or formula.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
