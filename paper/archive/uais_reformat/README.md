# UAIS submission package (Springer svjour3 format)

This folder contains the manuscript pre-converted to Springer's `svjour3`
class for *Universal Access in the Information Society*. The class file
itself is **not** in MiKTeX's default repository, so it must be downloaded
once from Springer.

## One-time setup: download svjour3.cls

1. Open: <https://resource-cms.springernature.com/springer-cms/rest/v1/content/19238/data/v8>
   (or search ``Springer LaTeX template svjour3'' and pick the journal package)
2. Extract the zip and copy these files **into this folder** (`paper/uais/`):
   - `svjour3.cls`
   - `spbasic.bst`
3. That's it.

(Alternatively, place the two files anywhere on the LaTeX search path —
e.g. `~/texmf/tex/latex/svjour3/` — and run `texhash`.)

## Compile

From inside `paper/uais/`:

```
xelatex main.tex
bibtex main
xelatex main.tex
xelatex main.tex
```

Korean (kotex) requires xelatex, not pdflatex. The two bibtex+xelatex
passes resolve cross-references and the numeric `spbasic` citation style.

Output: `main.pdf`.

## What's different vs the IEEEtran version

| Aspect | IEEEtran (`paper/main.tex`) | svjour3 (this folder) |
|---|---|---|
| Class | `IEEEtran` (2-column) | `svjour3` (1-column) |
| Author block | `\author` + `\thanks` footnotes | `\author` + `\institute` |
| Keywords | `keywords` environment | `\keywords{ \and ... \and ...}` macro |
| Bibliography | hand-coded `thebibliography` | external `refs.bib` + `\bibliographystyle{spbasic}` |
| Acknowledgments | `\section*{Acknowledgments}` | `acknowledgements` environment |
| Author bio | `IEEEbiography` env | omitted (UAIS does not request) |
| Figure width | `\columnwidth` (half page) | `0.95\textwidth` (full page) |
| Page count | 8 pages | ~14–18 pages (1-column inflates) |

## Files in this folder

| File | Status |
|---|---|
| `main.tex` | Pre-converted manuscript ready for svjour3 |
| `refs.bib` | Bibliography (19 entries) |
| `fig_pipeline.{pdf,png}` | Fig 1 |
| `fig_encoding_example.{pdf,png}` | Fig 2 |
| `fig_dataset_stats.{pdf,png}` | Fig 3 |
| `fig_section_coverage.{pdf,png}` | Fig 4 |
| `fig_webui.{pdf,png}` | Fig 5 |
| `svjour3.cls` | **DOWNLOAD** (see setup above) |
| `spbasic.bst` | **DOWNLOAD** (see setup above) |

## Before clicking Submit on the Editorial Manager

1. **ORCID** — replace the placeholder `0000-0000-0000-0000` on line ~28 of
   `main.tex` with the author's real ORCID iD (5 minutes to register at
   <https://orcid.org>).
2. **Compile once** to confirm svjour3 renders without errors.
3. Upload to UAIS Editorial Manager:
   - **Manuscript**: `main.pdf`
   - **LaTeX source**: zip of this whole folder (after running compile)
   - **Cover letter**: paste the contents of `../cover_letter.md` into
     the cover-letter text box
   - **Supplementary**: `../supplementary.zip`
