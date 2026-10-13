#!/usr/bin/env python3
"""Convert the PDFs fetched by gd_fetch.py into Markdown.

  constitution/grenada-constitution-act-cap-128a.md   (Constitution, Cap. 128A)
  chapters/cap-NNN-<slug>.md   chapters of the Revised Laws of Grenada
  acts/<year>/<slug>.md        annual Acts 2011-
Scans without text layer are listed in _raw/gd/gaps.json.
Usage: gd_convert.py
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gd_pdf2md  # noqa: E402
from gd_fetch import RAW, fname  # noqa: E402

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TODAY = datetime.date.today().isoformat()


def slug(s, n=80):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().replace("&", " and ")).strip("-")
    return s[:n].rstrip("-")


def yq(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def title_case(t):
    small = {"and", "of", "the", "for", "to", "in", "on", "by", "or", "at", "a", "an", "with"}
    words = t.lower().split()
    out = []
    for i, w in enumerate(words):
        if i and w in small:
            out.append(w)
        else:
            out.append(re.sub(r"^([(\"']?)([a-z])", lambda m: m.group(1) + m.group(2).upper(), w))
    return " ".join(out)


def main():
    idx = json.load(open(os.path.join(RAW, "index.json")))
    gaps, counts, used = [], {}, set()
    for it in idx:
        pdf = os.path.join(RAW, "pdf", fname(it))
        label = it.get("category") or it["doc_title"]
        if not os.path.exists(pdf):
            gaps.append({"title": label, "url": it["download"], "reason": "download failed"})
            continue
        pages = gd_pdf2md.pages_of(pdf)
        if gd_pdf2md.is_scan(pages):
            txt = " ".join("".join(pages).split())
            stub = re.search(r"\b(Repealed by|Spent|Amended by)\b.*$", txt)
            gaps.append({"title": label, "url": it["download"],
                         "reason": ("stub: " + stub.group(0)) if stub else "scanned PDF without text layer"})
            continue
        body = gd_pdf2md.convert(pages)
        meta = {}
        if it["kind"] == "chapter":
            m = re.match(r"CHAPTER\s+(\d+)([A-Z]*)\s+(.*)$", it["category"].strip(), re.I)
            num, suf, name = (int(m.group(1)), m.group(2).upper(), m.group(3)) if m else (0, "", it["category"])
            title = title_case(name.strip())
            cap = "%d%s" % (num, suf)
            if num == 128 and suf == "A":
                path = os.path.join(OUT, "constitution", "grenada-constitution-act-cap-128a.md")
                typ = "constitution"
            else:
                path = os.path.join(OUT, "chapters", "cap-%03d%s-%s.md" % (num, suf.lower(), slug(name)))
                typ = "act"
            m2 = re.search(r"Revised Edition\s+showing the law as at (\d{1,2} \w+ \d{4})", " ".join(pages[:2]))
            last = ""
            if m2:
                try:
                    last = datetime.datetime.strptime(m2.group(1), "%d %B %Y").date().isoformat()
                except ValueError:
                    pass
            meta = {"identifier": "Cap. " + cap, "type": typ, "last_amended": last}
        else:
            t = re.sub(r"\s+", " ", it["doc_title"]).strip()
            m = re.match(r"Act\s+No\.?\s*(\d+)\s+(?:of\s+(\d{4})\s+)?(.*)$", t, re.I)
            if m:
                no, yr, name = m.group(1), m.group(2) or it["year"], m.group(3)
                title = name.strip()
                ident = "Act No. %s of %s" % (no, yr)
                fn = "act-%02d-%s" % (int(no), slug(name, 70))
            else:
                title, ident, fn = t, "", slug(t, 80)
            path = os.path.join(OUT, "acts", it["year"], fn + ".md")
            meta = {"identifier": ident, "type": "act", "year": it["year"]}
        base, k = path, 2
        while path in used:
            path = base[:-3] + "-%d.md" % k
            k += 1
        used.add(path)
        fm = ["---", "title: " + yq(title)]
        if meta.get("identifier"):
            fm.append("identifier: " + yq(meta["identifier"]))
        fm += ["type: " + meta["type"], "jurisdiction: gd", "language: en"]
        if meta.get("year"):
            fm.append("year: " + yq(meta["year"]))
        if meta.get("last_amended"):
            fm.append("last_amended: " + meta["last_amended"])
        fm += ["status: in_force", "source: " + yq(it["download"]), "source_page: " + yq(it["category_url"]),
               "retrieved: " + TODAY, "---"]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(fm) + "\n\n# " + title + "\n\n" + body)
        counts[meta["type"] if it["kind"] == "chapter" else "annual act"] = counts.get(
            meta["type"] if it["kind"] == "chapter" else "annual act", 0) + 1
    json.dump(gaps, open(os.path.join(RAW, "gaps.json"), "w"), indent=1)
    print(counts, "gaps:", len(gaps))


if __name__ == "__main__":
    main()
