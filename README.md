# leakcalc

Reference implementations of published methods for estimating the energy saved by
repairing compressed-air leaks, each checked against the worked examples printed in
its source.

Industrial energy assessments, utility incentive programs and evaluators estimate
leak-repair savings with several different published methods. Applied to the same
leak with each source's own defaults, they can give results that differ by a factor
of about three (see [docs/algorithm_comparison.md](docs/algorithm_comparison.md)).
leakcalc puts these methods side by side, with each source's own constants and a page
reference for every equation. It does not pick a "best" method, and it does not claim
that any method is accurate for a particular plant.

## Methods

| Module | Source | What it implements |
|---|---|---|
| `leakcalc.essentials` | Muller et al., *Essentials of Industrial Assessments*, v3.0 (2015), pp. 188-198 | Choked (sonic) orifice flow; adiabatic compression power with compressor-type efficiencies; annual energy; the NBS leak table (Table 6.3) |
| `leakcalc.workbook` | Muller & Papadaratsakis, *Self-Assessment Workbook for Small Manufacturers*, v2.0 (2003), pp. 77-79 | Fliegner's formula for mass flow; isothermal compression energy; partial-load factor |
| `leakcalc.tipsheet` | U.S. DOE, *Compressed Air Tip Sheet #3: Minimize Compressed Air Leaks* (2004) | Leakage-rate table by pressure and orifice size, orifice correction factors, 18 kW per 100 cfm |
| `leakcalc.ump` | Benton, Burns & Zahlan, *UMP Chapter 22: Compressed Air Evaluation Protocol*, NREL/SR-7A40-77820 (2021), pp. 17-20 | Leak-down test (Eq. 11); simplified savings with the trim-compressor control adjustment factor CCAF (Eq. 12, Table 5) |
| `leakcalc.schmidt` | Schmidt & Kissock (2004) *Estimating Energy Savings in Compressed Air Systems*; Schmidt & Kissock (2005) ACEEE Summer Study, pp. 1-131 to 1-142 | Moss equation; linear part-load model FP = FP0 + (1 - FP0) FC; control-mode-corrected and "rule-of-thumb" savings |
| `leakcalc.compare` | — | Runs a selection of the methods above on one reference leak (scenario comparison) |

Full citations and page numbers are in each module's docstring.

## Install and use

Requires Python 3.9 or later. No third-party dependencies.

```bash
pip install .
```

```python
from leakcalc import essentials, tipsheet, ump

# Tip Sheet #3: one 1/8-inch sharp-edged leak at 100 psig, all year
cfm = tipsheet.leakage_cfm(1/8, 100, orifice="sharp")      # 15.38 cfm
kwh = tipsheet.annual_energy_kwh(cfm, hours=8760)          # 24,258 kWh/yr

# UMP Chapter 22 with a load/unload screw compressor (1 gal/cfm storage)
kwh_ump = ump.annual_energy_kwh(cfm, kw_full_load=67.5, cfm_rated=360, hours=8760,
                                ccaf="screw_load_unload_1gal_per_cfm")

# Essentials v3: choked-flow equation plus adiabatic compression power
r = essentials.leak_savings(1/8, line_psig=100, hours=8760, inlet_temp_f=70, line_temp_f=70,
                            adiabatic_eff=essentials.ADIABATIC_EFFICIENCY["rotary_screw"], motor_eff=0.90)
```

## Testing

```bash
python -m unittest discover -s tests -v
python tools/mutation_check.py      # deliberately breaks constants and formulas; every break must be caught
python tools/make_docs.py           # regenerates docs/*.md from the code
```

A GitHub Actions workflow ([.github/workflows/tests.yml](.github/workflows/tests.yml)) runs
`pip install .`, the unit tests and the mutation check on Python 3.9 to 3.13 for every push.

`tests/examples.py` holds 33 test cases drawn from six documents (five method
modules). Some are diagnostic variants of the same printed value. 25 reproduce the
printed value within its rounding. 8 do not; for each of these the notes separate
what the source shows from what is inferred about the cause. The equations were not
changed to force agreement. For those 8 cases the tests check two things: that the
mismatch is still there, and that leakcalc still returns the value stated in the
notes. So the record cannot drift silently, and a broken formula cannot pass merely
by disagreeing with the source. `tests/test_behaviour.py` adds checks that do not rely
on the package's own tables: hand-calculated values, a first-principles check of the
choked-flow constant, and input guards. See
[docs/worked_examples.md](docs/worked_examples.md).

Known limits of the checks:
- Values read from figures (Schmidt & Kissock 2005, Figure 2) were read by eye and are labelled approximate. They can only be checked against the original figure.
- Where two methods share one transcribed table (Tip Sheet #3 and UMP Table 6), a transcription error would affect both; the table was checked cell by cell against both sources.

## How this package was made

The code, tests and documentation were written with the help of AI tools (Anthropic
Claude). The author directed the work, chose the sources, and is responsible for the
content. The checks were:

- every equation and constant carries a page reference to the source it implements;
- every printed worked example that the package can recompute is a unit test;
- a mutation check (`tools/mutation_check.py`) breaks constants and formulas one at a time and confirms that the tests fail;
- a second AI model (OpenAI Codex) independently reviewed the code, tests and documentation against text extracts of the sources. Its report and the prompt it was given are in [docs/review/](docs/review/), and the changes made in response are listed in [docs/review/changes-2026-11-10.md](docs/review/changes-2026-11-10.md).

This is a personal project. It is not affiliated with, funded by or endorsed by any
employer, government agency or national laboratory.

## Relationship to MEASUR

The U.S. DOE's MEASUR tool includes a compressed-air leak survey calculator, with
estimate, decibel, bag and orifice methods. Its calculation library is
[ORNL-AMO/MEASUR-Tools-Suite](https://github.com/ORNL-AMO/MEASUR-Tools-Suite).
leakcalc is an independent implementation written from the published documents
listed above and contains no MEASUR code. For comparison, the relevant MEASUR source
files at commit `6cdc87c` were read, not copied. With equal inlet and line
temperatures, MEASUR's orifice method uses the same choked-flow relation as the
Essentials equation; their results differ by about 0.005 %, because of the rounded
constant 28.37 and the use of 460 versus 459.67. leakcalc checks that physics
independently in `tests/test_behaviour.py`.

## Scope and limits

- Only the methods above. The UMP CFM-bin method and multi-compressor systems are not implemented.
- UMP Equation 12 applies only to a single trim compressor in a system that is well controlled and operates predictably (UMP p. 18).
- Estimating a leak's size by ear or with an ultrasonic detector is outside the package. UMP Chapter 22 (p. 26) says ultrasonic detectors "should not be relied upon for quantifying the rate of leakage".

## Citation

If you use leakcalc, please cite it using the metadata in [CITATION.cff](CITATION.cff).

## License

MIT; see [LICENSE](LICENSE).
