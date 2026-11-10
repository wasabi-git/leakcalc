"""Mutation check for the test suite: break one constant or formula at a time in a
temporary copy of the package and confirm that the tests fail.

A test suite that still passes after a deliberate error is not evidence of correctness.

Run:  python -I -B tools/mutation_check.py      (writes tools/mutation_log.txt)
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _write(path, text):
    """UTF-8 with LF line endings (works on Python 3.9; Path.write_text(newline=) needs 3.10)."""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


ROOT = Path(__file__).resolve().parents[1]

MUTANTS = [
    ("essentials.py", "C4_SONIC = 28.37", "C4_SONIC = 28.0", "Essentials sonic constant"),
    ("essentials.py", "/ (IN2_PER_FT2 * math.sqrt(f_to_rankine(line_temp_f))))",
     "/ (IN2_PER_FT2 * f_to_rankine(line_temp_f) ** 0.5 * 1.01))", "Essentials flow off by 1 %"),
    ("essentials.py", "return work / (adiabatic_eff * motor_eff)", "return work / adiabatic_eff", "Essentials drops motor efficiency"),
    ("essentials.py", "C8_MMBTU_PER_HP_H = 0.002545", "C8_MMBTU_PER_HP_H = 0.0025", "Essentials C8"),
    ("workbook.py", "FLIEGNER_CONSTANT = 1915.2", "FLIEGNER_CONSTANT = 1900.0", "Fliegner constant"),
    ("workbook.py", "math.log(p2_psia / p1_psia)", "math.log10(p2_psia / p1_psia)", "ln replaced by log10"),
    ("tipsheet.py", "100: (0.40, 1.55, 6.31, 25.22, 100.9, 227.0),", "100: (0.40, 1.55, 6.31, 25.2, 100.9, 227.0),", "table typo 25.22 -> 25.2"),
    ("tipsheet.py", '"sharp": 0.61', '"sharp": 0.62', "sharp-orifice factor"),
    ("ump.py", '"screw_variable_speed": 0.97,', '"screw_variable_speed": 0.9,', "CCAF value"),
    ("ump.py", "return leak_scfm * kw_full_load / cfm_rated * hours * ccaf",
     "return leak_scfm * kw_full_load / cfm_rated * hours", "CCAF ignored"),
    ("schmidt.py", "(math.sqrt(MOSS_TEMP_R) * MOSS_DENSITY)", "(MOSS_TEMP_R * MOSS_DENSITY)", "Moss without square root"),
    ("schmidt.py", "return fp0 + (1.0 - fp0) * fc", "return fp0 + (1.0 - fp0) * fc * 1.02", "FP-FC slope"),
    ("schmidt.py", "KW_PER_HP_AS_PRINTED = 0.75", "KW_PER_HP_AS_PRINTED = 0.746", "printed 0.75 kW/hp replaced"),
    # added 2026-11-10 after the Codex review showed these survived the earlier suite
    ("ump.py", "LEAKDOWN_MULTIPLIER = 1.25", "LEAKDOWN_MULTIPLIER = 1.2", "leak-down multiplier (Eq. 11)"),
    ("essentials.py", "1 / 4: (40_300_000, 14.2),", "1 / 4: (40_300_000, 14.0),", "NBS table 1/4-in row"),
    ("tipsheet.py", "if abs(float(diameter_in) - float(d)) <= 1e-9:", "if abs(float(diameter_in) - float(d)) <= 1e-2:",
     "table column match too loose"),
    # (weakening only the [0, 1] check is an equivalent mutant once negative reductions are rejected,
    #  so the mutant restores the whole pre-review guard)
    ("schmidt.py",
     "    if delta_cfm < 0:\n        raise ValueError(\"delta_cfm must be a reduction (>= 0)\")\n"
     "    fc_after = fc_before - delta_cfm / flc_cfm\n"
     "    if not (0.0 <= fc_after <= 1.0 and 0.0 <= fc_before <= 1.0):",
     "    fc_after = fc_before - delta_cfm / flc_cfm\n    if fc_after < 0 or fc_before > 1:",
     "FC range guard as before the review"),
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    lines, killed = [], 0
    for fname, old, new, label in MUTANTS:
        with tempfile.TemporaryDirectory(prefix="leakcalc_mut_") as td:
            dst = Path(td) / "leakcalc"
            shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("__pycache__", ".git"))
            f = dst / "src" / "leakcalc" / fname
            src = f.read_text(encoding="utf-8")
            if src.count(old) != 1:
                lines.append(f"INVALID  {label}: pattern found {src.count(old)} times in {fname}")
                continue
            f.write_text(src.replace(old, new), encoding="utf-8")
            r = subprocess.run([sys.executable, "-I", "-B", "-m", "unittest", "discover", "-s", "tests"],
                               cwd=dst, capture_output=True, text=True)
            caught = r.returncode != 0
            killed += caught
            last = [x for x in r.stderr.splitlines() if x.startswith(("FAILED", "OK"))]
            lines.append(f"{'CAUGHT ' if caught else 'MISSED '}  {label} ({fname}): {last[-1] if last else ''}")
    out = f"Mutation check: {killed} of {len(MUTANTS)} deliberate errors caught by the tests\n" + "\n".join(lines) + "\n"
    print(out)
    _write(ROOT / "tools" / "mutation_log.txt", out)
    sys.exit(0 if killed == len(MUTANTS) else 1)


if __name__ == "__main__":
    main()
