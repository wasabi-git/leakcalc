You are an independent technical reviewer. Read-only: do not modify any file. Everything you need is in this folder.

Folder contents
- `leakcalc/` — a small Python package (stdlib only) implementing published methods for estimating energy saved by repairing compressed-air leaks: `src/leakcalc/*.py`, tests in `tests/` (worked examples in `tests/examples.py`), `tools/mutation_check.py`, generated docs in `docs/`, `README.md`, `LICENSE`, `CITATION.cff`, `pyproject.toml`. Author names are redacted as AUTHOR on purpose.
- `sources/` — text extractions (Markdown) of the five source documents the package cites. Each page starts with a marker `〔PDF 页 N〕` (= "PDF page N"); printed page numbers appear in `〔页脚〕`/`〔页眉〕` (footer/header) lines. Notes in Chinese inside parentheses are extraction notes, not source text.
- `measur_6cdc87c/` — files from the MEASUR-Tools-Suite repository (ORNL-AMO) at commit 6cdc87cbe596b110eadeb6da68352a8219bfc52f, keeping their repository paths; plus `constants.h` (= include/physics/constants.h) and the repository's only issue template.
- `desktop_14b4d35/` — two files from ORNL-AMO/AMO-Tools-Desktop at commit 14b4d351fa52b4c775890ea4fb1d7615fecbe495 (paths: src/app/calculator/compressed-air/air-leak-survey/air-leak-survey-help/air-leak-survey-help.component.html and src/app/calculator/compressed-air/air-leak-survey/air-leak-survey.service.ts).
- `issue/` — a DRAFT issue to be filed on MEASUR-Tools-Suite (`MEASUR-计算库议题-草稿.md`; the Chinese header is internal notes, the English part is the issue), and the script + JSON that produced its numbers.

Review two things.

A. leakcalc (code, tests, README, docs)
1. For every implemented equation and constant: does it match the cited source, and is the cited page right? Quote the source line you checked against (file and PDF page marker). List every mismatch, including unit or rounding issues.
2. For each worked example in `tests/examples.py`: is the "printed" value really what the source prints, at the cited page? For the entries marked `match=False`, is the written explanation supported by the source, or is there a simpler explanation (for example a transcription or input error in leakcalc)?
3. Do the tests actually test what they claim? Any test that would still pass if the formula were wrong?
4. README and docs: any claim not supported by the code, tests or sources? Any wording that overstates (e.g. "validated", "accurate")? Is the description of the relationship with MEASUR / AMO-Tools-Suite accurate given the MEASUR files here?
5. Packaging problems that would block `pip install .` or a first public release (metadata, license file, version).
If you can run Python, you may run `python -m unittest discover -s tests` inside `leakcalc/` and `python tools/mutation_check.py`; report the output. Do not install anything.

B. The draft MEASUR issue (English part)
1. Check every factual statement and every line-number link against the files in `measur_6cdc87c/` and `desktop_14b4d35/`: does the cited line say/do what the draft says? Give file:line for each check. Flag any statement that is wrong, imprecise, or not verifiable from the files given.
2. Check every number in the issue against `issue/measur_issue_numbers.json`, and the source page references against `sources/`.
3. Tone: would a maintainer read any sentence as blame, condescension or overclaiming? Quote the sentence and propose a neutral rewrite.
4. Does it follow the repository's issue template (`ISSUE_TEMPLATE_suite-api-change.md`) sensibly?
5. Anything missing that a maintainer would need to act on it, or anything that should be cut to keep it short.

Output format (Markdown):
- Section A and Section B, each a numbered list of findings. For each finding: severity (must-fix / should-fix / minor), location (file:line), what is wrong, the evidence (quote with file and page/line), and a concrete fix.
- Then a short list of things you checked and found correct (so the authors know what was covered).
- Say plainly when something could not be checked from the files given. Do not guess.
