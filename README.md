# Grenada — LawCodex

Legislation of Grenada (including Carriacou and Petite Martinique) as plain Markdown. Part of
[LawCodex](https://github.com/LawCodex).

**Status: full.** The repo covers every chapter of the Revised Laws and every annual Act
2011–2026 published on the official site.

## What is covered

| Directory | Contents | Files |
|---|---|---|
| `constitution/` | Grenada Constitution Act (Cap. 128A; S.I. 1973 No. 2155), with the Constitution of Grenada in its Schedule | 1 |
| `chapters/` | Chapters of the Revised Laws of Grenada, `cap-NNN-<slug>.md` | 474 |
| `acts/<year>/` | Annual Acts 2011–2026 (all Acts listed, including appropriation, loan and amending Acts), `act-NN-<slug>.md` | 377 |

**Total: 852 texts.**

### Source

**Laws of Grenada**, Government of Grenada: https://laws.gov.gd/

- Chapters: https://laws.gov.gd/index.php/legislation. One sub-category per chapter, grouped
  by letter, each holding one PDF.
- Acts: https://laws.gov.gd/index.php/acts, one category per year.

The chapter PDFs are the consolidated Revised Laws prepared by the Law Revision Commissioner.
They are born-digital, so extraction quality is good. Some chapter PDFs bundle the
chapter's subsidiary legislation after the Act ("• Act • Subsidiary Legislation •"). That text
is kept as it appears in the PDF. Each file's `source` is the official download URL and
`source_page` is the listing page.

## What is not covered (gaps)

- **Statutory Rules and Orders** (S.R.&O. 2011–2026, about 700 items, at
  https://laws.gov.gd/index.php/s-r-o) are not included.
- Annual Acts before 2011 are not listed separately on the site. They are consolidated into
  the chapters.
- 29 chapter entries are one-line placeholders stating that the chapter was repealed, is
  spent, or (Cap. 49) was amended, with no text. They are not included: Cap. 3 Adoption Act (Repealed by Act No. 20 of 2010); Cap. 38A Business Levy Act (Repealed by Act No. 36 of 1994); Cap. 49 Church Of God Seventh Day (Incorporation) Act (Amended by Act No. 51 of 1980); Cap. 75 Customs Act (Repealed by Act No. 13 of 1991); Cap. 80 Department Of Labour Act (Repealed by Act No. 14 of 1999); Cap. 95 Excise (Generalcommodities) Act (Repealed by Act No. 4 of 2010); Cap. 100B Family Court Act (Repealed by Act No. 8 of 1996); Cap. 119 Fugitive Offenders Act (Repealed by Act No. 22 of 1998); Cap. 127 Grenada Broadcastingcorporation Act (Repealed by Act No. 8 of 1998); Cap. 135 Hospitals Act (Repealed by Act No. 4 of 1998); Cap. 139A House Of Representatives (Elections) Act (Repealed by Act No. 35 of 1993); Cap. 157 Labour Clauses (Public Contracts) Act (Repealed by Act No. 14 of 1999); Cap. 187 Maternity Leave Act (Repealed by Act No. 14 of 1999); Cap. 194 Midwives Act (Repealed by Act No. 15 of 2003); Cap. 196 Misuse Of Drugs Act (Repealed by Act No. 7 of 1992); Cap. 206A National Reconstruction Levy Act (Repealed by Act No. 1 of 2009); Cap. 248 Post Office Act (Repealed by Act No. 21 of 1996); Cap. 262C Public Half-Holiday (13Th August) Act (Spent); Cap. 276 Real Property Tax Act (Repealed by Act No. 2 of 1997); Cap. 304 Shop Hours Act (Repealed by Act No. 14 of 1999); Cap. 322 Town Andcountry Planning Act (Repealed by Act No. 25 of 2002); Cap. 324 Trade Disputes (Arbitration And Inquiry) Act (Repealed by Act No. 15 of 1999); Cap. 325 Trade Unions Recognition Act (Repealed by Act No. 15 of 1999); Cap. 326 Trade Unions And Trade Disputes Act (Repealed by Act No. 15 of 1999); Cap. 328 Treasury Bills Act (Repealed by Act No. 4 of 2003); Cap. 334 Wagescouncils Act (Repealed by Act No. 14 of 1999); Cap. 335 Weights And Measures Act (Repealed by Act No. 18 of 1997); Cap. 342 Wireless Telegraphy Act (Repealed by Act No. 31 of 2000); Cap. 343 Workman'S Compensation Act (Repealed by Act No. 11 of 1998).
- No PDF lacked a text layer, so nothing needed OCR.

## Format

One Markdown file per law with YAML front matter (`title`, `identifier` (Cap. number or
"Act No. N of YYYY"), `type`, `jurisdiction`, `language`, `year`, `status`, `source`,
`source_page`, `retrieved`). Text was extracted with `pdftotext` and kept as extracted.
Running headers and page numbers were removed. PART / CHAPTER / SCHEDULE lines become `##`
headings and section numbers become `### N.` headings. In the PDFs the section title
(marginal note) often comes on the line after the number.

## Licence / copyright

Official legislative texts of Grenada, published by the Government of Grenada for free public
access. No terms restricting reuse were found on the site. This is not an official
publication.

## Regenerate

```sh
pip install -r scripts/requirements.txt   # plus poppler-utils
python3 scripts/gd_fetch.py     # index + PDFs into ../_raw/gd (1.5 s between requests)
python3 scripts/gd_convert.py   # Markdown
```

Note: the site's document manager remembers the list offset in the session, so the fetcher
always passes an explicit `?start=N` and clears cookies.

Retrieved: 2026-10-13.
