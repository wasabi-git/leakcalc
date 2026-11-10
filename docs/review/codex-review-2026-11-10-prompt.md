> Note: the original prompt also asked the reviewer to check a separate draft document (part B, with its supporting folders). It is not part of this package, so those lines are not included here; the remaining text is unchanged.

You are an independent technical reviewer. Read-only: do not modify any file. Everything you need is in this folder.

Folder contents
- `leakcalc/` — a small Python package (stdlib only) implementing published methods for estimating energy saved by repairing compressed-air leaks: `src/leakcalc/*.py`, tests in `tests/` (worked examples in `tests/examples.py`), `tools/mutation_check.py`, generated docs in `docs/`, `README.md`, `LICENSE`, `CITATION.cff`, `pyproject.toml`. Author names are redacted as AUTHOR on purpose.
- `sources/` — text extractions (Markdown) of the five source documents the package cites. Each page starts with a marker `〔PDF 页 N〕` (= "PDF page N"); printed page numbers appear in `〔页脚〕`/`〔页眉〕` (footer/header) lines. Notes in Chinese inside parentheses are extraction notes, not source text.
- `measur_6cdc87c/` — files from the MEASUR-Tools-Suite repository (ORNL-AMO) at commit 6cdc87cbe596b110eadeb6da68352a8219bfc52f, keeping their repository paths; plus `constants.h` (= include/physics/constants.h) and the repository's only issue template.

Review two things.

A. leakcalc (code, tests, README, docs)
1. For every implemented equation and constant: does it match the cited source, and is the cited page right? Quote the source line you checked against (file and PDF page marker). List every mismatch, including unit or rounding issues.
2. For each worked example in `tests/examples.py`: is the "printed" value really what the source prints, at the cited page? For the entries marked `match=False`, is the written explanation supported by the source, or is there a simpler explanation (for example a transcription or input error in leakcalc)?
3. Do the tests actually test what they claim? Any test that would still pass if the formula were wrong?
4. README and docs: any claim not supported by the code, tests or sources? Any wording that overstates (e.g. "validated", "accurate")? Is the description of the relationship with MEASUR / AMO-Tools-Suite accurate given the MEASUR files here?
5. Packaging problems that would block `pip install .` or a first public release (metadata, license file, version).
If you can run Python, you may run `python -m unittest discover -s tests` inside `leakcalc/` and `python tools/mutation_check.py`; report the output. Do not install anything.

Output format (Markdown):
- Section A and Section B, each a numbered list of findings. For each finding: severity (must-fix / should-fix / minor), location (file:line), what is wrong, the evidence (quote with file and page/line), and a concrete fix.
- Then a short list of things you checked and found correct (so the authors know what was covered).
- Say plainly when something could not be checked from the files given. Do not guess.
