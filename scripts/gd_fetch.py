#!/usr/bin/env python3
"""Fetch the Laws of Grenada from laws.gov.gd (Government of Grenada,
Ministry of Legal Affairs; Joomla + Edocman document manager).

  * /index.php/chapters/<letter-range>: one sub-category per chapter of the
    Revised Laws of Grenada (2010 revision, updated), each holding one PDF;
  * /index.php/acts/<id>-<year>: annual Acts 2011-, paginated by 20.
PDFs are cached in _raw/gd/pdf/. robots.txt allows everything and sets no
Crawl-delay; we wait 1.5 s between requests anyway.
Usage: gd_fetch.py
"""
import html as htmlmod
import json
import os
import re
import subprocess
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://laws.gov.gd"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
RAW = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "_raw", "gd"))
DELAY = 1.5
s = requests.Session()
s.headers["User-Agent"] = UA


def get(url):
    for i in range(5):
        try:
            r = s.get(url, timeout=300)
            time.sleep(DELAY)
            if r.status_code in (200, 404, 403, 410):
                return r
        except requests.RequestException as e:
            print("  retry", url, e, file=sys.stderr, flush=True)
        time.sleep(5 * (i + 1))
    raise RuntimeError("failed " + url)


class _Failed:
    status_code = 0
    content = b""
    headers = {}


FAILED = _Failed()


def pdf_ok(path):
    if not os.path.exists(path) or os.path.getsize(path) < 100:
        return False
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(max(0, os.path.getsize(path) - 2048))
        tail = f.read()
    if head != b"%PDF-" or b"%%EOF" not in tail:
        return False
    return subprocess.run(["pdfinfo", path], capture_output=True).returncode == 0


def docs_on(url):
    """Download links + titles on an edocman category page (all pages)."""
    out, start = [], 0
    while True:
        u = url + "?start=%d" % start  # explicit: edocman remembers the offset in the session
        s.cookies.clear()
        for attempt in range(4):
            r = get(u)
            if r.status_code == 200 and "</html>" in r.text[-2000:] and "edocman" in r.text:
                break
            print("  incomplete page, retrying", u, r.status_code, flush=True)
            time.sleep(10)
        soup = BeautifulSoup(r.text, "lxml")
        got = 0
        for a in soup.select("a.edocman-document-title-link"):
            href = a["href"]
            if href.endswith("/download"):
                out.append({"download": BASE + href, "doc_title": a.get_text(" ", strip=True)})
                got += 1
        if got and soup.find("a", href=re.compile(r"start=%d\b" % (start + 20))):
            start += 20
            continue
        return out, soup


def build_index():
    ip = os.path.join(RAW, "index.json")
    if os.path.exists(ip):
        return json.load(open(ip))
    idx = []
    soup = BeautifulSoup(get(BASE + "/index.php/legislation").text, "lxml")
    letters = sorted({a["href"] for a in soup.find_all("a", href=re.compile(r"^/index.php/chapters/[a-z]-[^/]+$"))})
    for L in letters:
        _, ls = docs_on(BASE + L)
        subs = []
        for a in ls.select("a.edocman-category-title-link"):
            if a["href"].startswith(L + "/") and a["href"] not in [x[0] for x in subs]:
                subs.append((a["href"], a.get_text(" ", strip=True)))
        for href, title in subs:
            docs, _ = docs_on(BASE + href)
            for d in docs:
                d.update({"kind": "chapter", "category": title, "category_url": BASE + href})
                idx.append(d)
            print("chapter", title, len(docs), flush=True)
    soup = BeautifulSoup(get(BASE + "/index.php/acts").text, "lxml")
    years = sorted({a["href"] for a in soup.find_all("a", href=re.compile(r"^/index.php/acts/\d+-\d{4}$"))})
    for y in years:
        docs, _ = docs_on(BASE + y)
        for d in docs:
            d.update({"kind": "act", "year": y[-4:], "category_url": BASE + y})
            idx.append(d)
        print("acts", y, len(docs), flush=True)
    json.dump(idx, open(ip, "w"), indent=1)
    return idx


def fname(d):
    m = re.search(r"/(\d+)-([^/]+)/download$", d["download"])
    return (m.group(1) + "-" + m.group(2))[:120] + ".pdf"


def main():
    os.makedirs(os.path.join(RAW, "pdf"), exist_ok=True)
    idx = build_index()
    print(len(idx), "documents", flush=True)
    bad = []
    for n, d in enumerate(idx):
        p = os.path.join(RAW, "pdf", fname(d))
        if pdf_ok(p):
            continue
        try:
            r = get(d["download"])
        except RuntimeError as e:
            print('  giving up', e, flush=True)
            r = FAILED
        ok = False
        if r.status_code == 200 and r.content[:5] == b"%PDF-":
            cl = r.headers.get("content-length")
            if not cl or r.headers.get("content-encoding") or int(cl) == len(r.content):
                open(p, "wb").write(r.content)
                ok = pdf_ok(p)
        if not ok:
            bad.append({"url": d["download"], "status": r.status_code, "ctype": r.headers.get("content-type")})
        print(n, fname(d), ok, r.status_code, flush=True)
    json.dump(bad, open(os.path.join(RAW, "failed.json"), "w"), indent=1)
    print("failed:", len(bad))


if __name__ == "__main__":
    main()
