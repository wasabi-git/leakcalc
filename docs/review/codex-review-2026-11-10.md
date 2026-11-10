## Section A — leakcalc

I found citation errors, overstated test coverage, and two input-validation defects. The implemented engineering equations otherwise agree with the supplied text, subject to the extraction limitations noted below. No files were modified.

Source abbreviations used below:

| Abbreviation | File under `sources/` |
|---|---|
| E | `Essentials_of_Industrial_Assessments_v3.md` |
| W | `Self-Assessment_Workbook_for_SMMs_v2.0.md` |
| T | `DOE_CompressedAir_TipSheet3_MinimizeLeaks_2004.md` |
| U | `Benton2021_UMPCh22_CompressedAir_NREL77820.md` |
| S04 | `Schmidt2004_EstimatingSavingsCompressedAir.md` |
| S05 | `Schmidt2005_ModelingAirCompressorEnergyUse_ACEEE.md` |

1. **Must-fix — Essentials PDF page references are systematically one page too high.**

   **Location:** `leakcalc/src/leakcalc/essentials.py:8–13,112`; `leakcalc/tests/examples.py:23–68`; corresponding rows in `docs/worked_examples.md`.

   The printed page numbers are correct, but the PDF page numbers are not:

   | Material | Printed page | Actual PDF marker | Currently cited PDF page |
   |---|---:|---:|---:|
   | Table 6.3 | 189 | 200 | 201 |
   | Case inputs | 192 | 203 | 204 |
   | Results and summary tables | 194 | 205 | 206 |
   | Flow equation | 195 | 206 | 207 |
   | Power equation and most constants | 196 | 207 | 208 |
   | Roots efficiency and motor-efficiency definition | 197 | 208 | 209 |
   | Annual energy equation | 198 | 209 | 210 |

   **Evidence:** E, `〔PDF 页 205〕`, line 6742: “`1/8   29.0   6.9   149.7   $2,103`”; that page ends with “`194 Modern Industrial Assessments`” at line 6768. The flow equation is under `〔PDF 页 206〕`, ending with printed page 195.

   There are also two Schmidt page errors:

   - `tests/examples.py:150`: SK04-6’s `$2,000` calculation is on **PDF page 6**, not page 5. S04:229: “`ESAV = 7 kW x 4,080 hr/yr x $0.07 /kWh = $2,000 /yr`.”
   - `src/leakcalc/schmidt.py:55–56`: the 60%–85% and 20%–60% ranges occur on **PDF page 5**, not page 6; see S04:187.

   **Fix:** Correct the references in the source data/docstrings, then regenerate the documentation.

2. **Must-fix — UMP-2’s “printed” value is calculated by leakcalc, not printed by the source. The coverage count also overstates the number of original examples.**

   **Location:** `leakcalc/tests/examples.py:118–121`; `leakcalc/README.md:59–65`; `leakcalc/docs/worked_examples.md:6,27,44`.

   UMP-2 sets `printed=25.22 * 0.61`, producing **15.3842**. The source prints **25.22** and separately supplies the correction factor.

   **Evidence:** U, `〔PDF 页 30〕`, line 966: “`100 … 25.22 …`”; line 969: “`Values should be multiplied by 0.97 for well-rounded orifices and by 0.61 for sharp orifices`.”

   Likewise, the 33 rows include repeated targets and diagnostic alternatives—ESS-2b, WB-1b, SK04-3b, SK04-4b and SK05-3b—rather than 33 distinct published worked examples. There are **six documents**, grouped into five method modules.

   **Fix:** Rename the column to “Source target / derived target,” explicitly classify UMP-2 as derived, and say “33 test cases drawn from six documents, including diagnostic variants.” Retain the accurate **25 expected matches / 8 expected mismatches** count without calling every row an original printed example.

3. **Should-fix — The mismatch tests establish disagreement, not correctness; several other tests provide little independent formula coverage.**

   **Location:** `leakcalc/tests/test_worked_examples.py:26–34`; `tests/test_behaviour.py:35–46,67–81`; `tests/examples.py:62–68`.

   Every `match=False` assertion accepts **any** result sufficiently different from the source target, including zero or NaN. It does not pin the documented recomputation.

   **Evidence:** `test_worked_examples.py:33` uses only:

   > `self.assertFalse(within(v, ex["printed"], ex["rtol"]))`

   Additional limitations:

   - ESS-4 checks arithmetic on copied table values; it never calls an implemented engineering equation.
   - ESS-5 checks copied energy × electricity price; it does not validate flow, power or annual-energy calculations.
   - UMP/Table-6 equality compares two functions that use the **same underlying table**, so a shared transcription error survives.
   - Diameter-squared scaling survives any erroneous multiplicative constant.
   - The comparison test pins only the minimum and maximum energy values; intermediate rows can change without detection.

   **Observed counterexamples:** All 44 tests still passed when, in memory, I replaced `ump.leakdown_scfm` with a function returning `999`, and separately when I changed the NBS 1/4-inch energy value from **14.2 to 999**.

   **Fix:** Assert the documented calculated value as well as disagreement for mismatch cases. Add independent numerical checks for Equation 11, the complete NBS table, and currently unverified table entries/constants. Describe arithmetic and consistency tests according to what they actually establish.

4. **Should-fix — The explanations of source discrepancies need clearer separation between observation and inference.**

   **Location:** `leakcalc/tests/examples.py:46–57,73–79,112–113,132–145,175–185`; generated notes in `docs/worked_examples.md`.

   I checked all eight `match=False` cases:

   | Case | What the supplied source supports | Assessment / concrete fix |
   |---|---|---|
   | ESS-1 | E, PDF 203, gives Ti 92°F, Tl 72°F and 115 psig; PDF 205 prints 29.0 cfm. The implemented equation gives **24.504954**. | The disagreement is real, and leakcalc’s inputs match. Ratios across 1/32–3/8 inch are **1.175273–1.183434**. Replace “the table was made with a different constant or input” with “the cause is undetermined”; arithmetic or source transcription errors are also possible. |
   | ESS-2 | E, PDF 207: denominator “`Ea × Em`”; PDF 203: motor efficiency 91.5%. | **7.486673 hp** follows the equation; omitting motor efficiency gives **6.850306 hp**. “Appears to omit” is appropriately tentative. |
   | WB-1b | W, PDF 83: prose says “`line pressure of 110 psi`,” while the substitution explicitly uses “`114.7 psia`.” | The source contains the input inconsistency. **329.465606 lbm/h** at 124.7 psia is correct. No simpler leakcalc input error found. |
   | TS-4 | T, PDF 2: printed lines are $5,611, $10,991 and $38,776; total printed is $57,069. | The discrepancy is real: printed lines sum to **$55,378**, unrounded calculations to **$55,377.63**. The “almost 70%” wording is corroborative at most; it does not prove the cause. |
   | SK04-3 | S04, PDF 8: the expression explicitly uses **0.75 kW/hp** and prints $3,945. | The expression gives **$3,966.67**. Using 0.746 gives **$3,945.51**, which rounds to $3,946 to the nearest dollar. Say “approximately consistent with a less-rounded horsepower conversion,” rather than implying exact reproduction. |
   | SK04-4b | S04, PDF 8–9: FC is rounded to 47%, then 21%, then FP to 85%; savings printed are 2.8 kW. | The rounding explanation is supported. **2.609811 kW** is the consistent linear-model result for a 70/265 capacity reduction. |
   | SK05-3 | S05, PDF 5, obtains FC 65.5%; PDF 6 then uses “`C = 265 scfm x 47% = 125 cfm`.” | The source changes baseline. **15,933.585 kWh/year** is the consistent-model result. The written explanation is supported. |
   | SK05-4 | S05, PDF 6: “`the electricity savings would be about 42,000 kWh/yr`.” No intermediate load/unload calculation is shown. | **24,724.528 kWh/year** follows the consistent model. The proposed 44−33.5 kW reconstruction is plausible, but the source does not establish that this was its calculation. Label it a possible reconstruction. |

   **Fix:** Preserve the discrepancies, but qualify explanations that the source does not explicitly establish.

5. **Should-fix — One further Workbook input inconsistency is omitted from the example notes.**

   **Location:** `leakcalc/tests/examples.py:84–89`; `leakcalc/docs/worked_examples.md:19–20`.

   WB-3 and WB-4 correctly follow the numerical substitution using 90°F, but the immediately preceding prose says 95°F.

   **Evidence:** W, `〔PDF 页 83〕`, line 2417:

   > “`It will be assumed to average 95ºF.`”

   Lines 2423 and 2428 instead use “`[90 + 460]`” and “`(550)`”.

   **Fix:** Add a note that these tests reproduce the **90°F substitution**, while the prose states 95°F. Do not describe the source inputs as wholly consistent.

6. **Must-fix — The table lookup silently accepts some unlisted diameters despite promising exact tabulated inputs only.**

   **Location:** `leakcalc/src/leakcalc/tipsheet.py:33–41`; inherited by `ump.table6_cfm`; similar selection logic in `compare.py:57,72`.

   `Fraction(diameter_in).limit_denominator(64)` can map an unlisted diameter to a listed one.

   **Evidence:** The docstring says “`Only the tabulated pressures and diameters are allowed`.” Yet `tipsheet.leakage_cfm(0.124, 100)` returns the 1/8-inch result, **15.3842 cfm**.

   T, PDF 1:69, lists the actual columns: “`1/64 1/32 1/16 1/8 1/4 3/8`.”

   **Fix:** Check membership against the actual permitted numeric diameters, or use a narrowly defined floating-point equality tolerance. Do not use denominator reduction as input validation. Add a rejection check for `0.124`.

7. **Should-fix — The Schmidt range guard does not enforce the range it claims.**

   **Location:** `leakcalc/src/leakcalc/schmidt.py:79–88`; `tests/test_behaviour.py:29–31`.

   It checks only `fc_after < 0` and `fc_before > 1`. It can accept an after-capacity above 1.

   **Evidence:** The exception says “`FC outside [0, 1]`,” but:

   ```python
   demand_reduction_kw(52, 265, 0.55, 0.5, -265)
   ```

   returns `fc_after=1.5` and negative savings.

   **Fix:** Check both endpoints against `[0,1]`; reject a negative `delta_cfm` if this API is specifically for demand reductions. The existing guard test covers only one invalid case.

8. **Should-fix — Applicability and comparison wording omit assumptions or imply a stronger controlled comparison than the code performs.**

   **Location:** `leakcalc/src/leakcalc/ump.py:15–17`; `src/leakcalc/compare.py:1–8,39–83`; `docs/algorithm_comparison.md:6,8,44,67–69`; `README.md:23`.

   - The UMP applicability summary omits the requirement that the system be well-controlled and predictable.
   - The source describes CCAF values as slopes over the **40%–80% capacity range**; that context is absent from the package’s CCAF description.
   - “The comparison holds the plant fixed and varies only the method” is too strong. Rows vary orifice geometry, load factor, compressor/control type, and compression assumptions.
   - “Runs every method” excludes the implemented leak-down method and several CCAF alternatives.
   - The table labels all flows “scfm,” although Essentials explicitly returns free-air cfm at the inlet conditions, and the Tip Sheet labels its table simply cfm.

   **Evidence:** U, PDF 28:873: “`The compressed air system is well-controlled and operates predictably`”; line 898: “`within the 40% to 80% capacity range`.” E, PDF 207:6821–6823, defines free-air volumetric flow and inlet temperature. T, PDF 1:65, labels its rates “`(cfm)`”.

   **Fix:** Describe the output as a **scenario comparison using alternative published assumptions**. State flow reference conditions explicitly, include the missing UMP qualifications, and replace “every method” with “selected applicable methods.”

9. **Minor — Small numerical departures from literal source constants are not fully disclosed.**

   **Location:** `leakcalc/src/leakcalc/units.py:10–11,20`; `src/leakcalc/essentials.py:87–95`; module-wide claims about preserving source constants.

   - Essentials prints π as **3.1416**, while the implementation uses `math.pi`. This changes area/flow by approximately **−0.000234%**.
   - The manual’s C8 converted using the package’s MMBtu factor is **0.74586587315 kWh/hp-h**, versus `KW_PER_HP=0.745699872`: approximately **0.02226%**, not the stated 0.03%.
   - `0.745699872` and `293.07107` are finite-precision conversion factors; calling them “exact” is unnecessary.
   - Their provenance is not cited in the supplied package.

   **Evidence:** E, PDF 207:6828: “`3.1416`”; PDF 209:6884: “`0.002545 MMBtu/hp-h`.”

   **Fix:** Document the π substitution and call the conversion factors standard rounded values. Change the stated difference to approximately **0.02%** and provide conversion provenance. These are small differences, not material engineering formula errors.

10. **Should-fix — Some visual-source claims cannot be verified from the supplied extractions.**

    **Location:** `leakcalc/src/leakcalc/schmidt.py:44–52,64`; related README/docs statements.

    The supplied files do not contain the original PDF page images. Consequently, I could not verify the five plotted FP0 intercepts—0.70, 0.60, 0.25, 0.10 and 0—or the claim that a page image visibly shows the Moss square root.

    **Evidence:** S05, PDF 3:93–105, contains chart labels but no recoverable plotted coordinates. S04, PDF 8:303–311, has the flattened denominator “`530(R) x 0.07494`.” A square root is consistent with the printed 3.96 result, but the image itself is unavailable.

    **Fix:** Retain “approximate figure readings,” but distinguish an author’s prior visual inspection from verification possible with these files. Preserve a page image or explicit digitization evidence for reproducible review.

11. **Should-fix — The MEASUR relationship paragraph mixes repository names and includes unverifiable provenance claims.**

    **Location:** `leakcalc/README.md:69–76`.

    The supplied current calculation-library files are from **MEASUR-Tools-Suite**, whereas the README names **AMO-Tools-Suite**. The four measurement branches are supported by the supplied code, and the sonic-flow relationship is supported mathematically. However, this folder does not establish the historical repository relationship, upstream licensing, or the assertion that upstream code was read “only” for this paragraph.

    **Evidence:** `measur_6cdc87c/src/compressedAir/leak_survey/compressed_air_leak_survey.cpp:15–35` routes estimate, decibels, bag and orifice methods. No upstream LICENSE or development history is supplied.

    **Fix:** Name the reviewed repository and commit precisely. Say that leakcalc implements published equations independently; avoid unverifiable historical/process claims. Keep any upstream copyright/license description only with supporting evidence.

12. **Should-fix for release metadata; minor for tooling — No obvious static install blocker, but remove the placeholder ORCID and resolve the advertised Python-version inconsistency.**

    **Location:** `leakcalc/CITATION.cff:13`; `README.md:29,55–56`; `tools/mutation_check.py:57`; `tools/make_docs.py:116–117`.

    The CFF contains the placeholder identifier `https://orcid.org/0000-0000-0000-0000`. Separately, the documented tooling uses `Path.write_text(..., newline=...)`, which requires Python 3.10+, while the README advertises Python 3.9+.

    **Evidence:** The cited tooling lines pass `newline="\n"`.

    **Fix:** Remove or replace the ORCID. Either make the tools compatible with 3.9 or state their higher requirement separately.

    The intentional `AUTHOR` redactions are **not findings**. Version **0.1.0** agrees across `pyproject.toml`, `__init__.py` and `CITATION.cff`. The MIT license text is complete, and the `src` package-discovery configuration appears appropriate. I did not build or install, so actual wheel/sdist contents and installation remain unverified.

## Section B — draft MEASUR issue

Here, `draft` means `issue/MEASUR-计算库议题-草稿.md`; `M/` means `measur_6cdc87c/`; `D/` means `desktop_14b4d35/`.

1. **Must-fix — The opening overstates what was validated, and example (a) is not a published worked example.**

   **Location:** `draft:38,92–106,127`.

   > “**I did not find a calculation error.** The equations reproduce the published worked examples listed below.”

   This is broader than the evidence:

   - Suite values were obtained from a Python transcription, not a compiled-library run.
   - Case (a)—1/8 inch, 100 psig, equal 70°F temperatures—is a synthetic equation check. Essentials’ actual case inputs are 115 psig, 92°F inlet and 72°F line temperature.
   - Case (b) matches UMP only **after an external 0.97 adjustment**.
   - Case (c) checks the conversion of an entered estimate; it does not validate Suite’s orifice-flow calculation.

   **Evidence:** E, PDF 203:6705–6709, gives “`92`,” “`115`,” “`72`,” and “`115`” for those case inputs. `M/src/compressedAir/leak_survey/compressed_air_leak_survey.cpp:44` does not apply CCAF.

   “The comparison is exact only when the two are equal” at line 106 is also imprecise: even at equal temperatures, the stated constants produce **20.8454917572 versus 20.8464451050**, a **−0.004573%** difference.

   **Fix / neutral rewrite:**

   > “I identified three documentation clarifications. A Python transcription of the supplied calculation code agrees closely with the Essentials flow equation for equal temperatures, and reproduces the UMP and Tip Sheet examples with the adjustments described below. I have not run the compiled library.”

   Call (a) an **equation-derived test case**, and say the formulations agree **up to the stated constant/conversion differences** when temperatures are equal.

2. **Must-fix — The proposed CCAF instruction confuses a fractional source factor with a percentage-valued API field.**

   **Location:** `draft:53`.

   > “To obtain leak-repair savings as in UMP Chapter 22 Eq. 12, multiply by CCAF/100…”

   UMP’s CCAF is **0.97**, while the Desktop percentage field is **97**. Dividing the UMP value by 100 would introduce a hundredfold error.

   **Evidence:** U, PDF 29:934: “`CCAF … = 0.97`.” `D/air-leak-survey.service.ts:171` applies `compressorControlAdjustment / 100`.

   **Fix / neutral rewrite:**

   > “The survey does not apply `compressor_control_adjustment`. For savings, multiply the unadjusted electricity reduction by `compressor_control_adjustment / 100`—for example, 97/100 for UMP CCAF 0.97.”

3. **Should-fix — Qualify the claim of application-wide UMP consistency.**

   **Location:** `draft:51`.

   > “So the end result in the app is consistent with UMP Chapter 22, Eq. 12…”

   The shown service applies the right algebraic factor **in the electricity branch**, but that alone does not verify the complete application, field mapping, units, selected defaults or UMP applicability.

   **Evidence:** `D/air-leak-survey.service.ts:168–173` conditions this on `utilityType === 1`. The wrapper and conversion implementations called at lines 121–141 are not supplied. U, PDF 28:873–877, imposes operating-condition restrictions.

   **Fix / neutral rewrite:**

   > “For electricity savings, this service applies a percentage factor after the Suite calculation, matching the algebraic form of UMP Eq. 12 when the entered specific power and CCAF are appropriate.”

4. **Should-fix — Several repository-wide, historical and policy claims cannot be established from the supplied files.**

   **Location:** `draft:34,38,70,80,85,90,94,110,114`.

   | Claim | What can actually be checked | Concrete fix |
   |---|---|---|
   | Quick turnaround on #401 | No issue history supplied. | Remove the reference or verify independently before posting. |
   | Commit was `develop` on 2026-11-10 | The supplied commit identity is given, but branch/date metadata is absent. | Cite the commit alone. |
   | “the leak survey `.dox` pages cite nothing” | Only the orifice `.dox` page is supplied; it has no bibliographic citations. | Say “the supplied orifice calculator page contains no bibliographic citations.” |
   | “no test pinned to a published worked example” | Neither supplied test file identifies such an example; the entire test repository is not present. | Scope the claim to the two reviewed files. |
   | Methods “trace to” the listed publications | Mathematical correspondence is demonstrated; historical provenance is not. | Say “relevant references supporting these equations and factors include…” |
   | Sourcebook, third edition | That document is not supplied. U’s bibliography instead lists a November 2003 sourcebook, which does not establish the proposed edition. | Omit the unverified edition entry or complete it from a verified copy before posting. |
   | Default specific-power provenance | Help lists typical values, but the default-data implementation is absent. | Ask for the source of the **help table’s values**, rather than asserting facts about all defaults. |
   | PR workflow and Desktop contribution policy | The referenced workflow and CONTRIBUTING files are absent. | Remove the policy assertions or verify them before posting. |
   | Separate email report | Sending/reporting status cannot be established from these files. | Use “I plan to report this separately” if that accurately describes the status. |

   **Evidence:** `D/air-leak-survey-help.component.html:444–460` lists **16, 20, 23 and 21 kW/100 scfm**. U:1574 lists the sourcebook as “`November 2003`.”

5. **Should-fix — The reproduced numbers are sound, but the supplied reproduction script is not portable and the public issue lacks a runnable Suite reproducer.**

   **Location:** `draft:40,146–165`; `issue/measur_issue_numbers.py:17–18,105–107`.

   The script refers to the previous project layout:

   > `ROOT / "08-开源工具" / "leakcalc" / "src"`

   It also writes to another old-layout directory. Neither matches this supplied folder. The English reproduction block reproduces leakcalc values only; it does not contain the Suite transcription used for the “Suite” columns.

   **Evidence:** The complete transcription is available at `issue/measur_issue_numbers.py:29–44`, but is not included in the English issue.

   **Fix:** Attach a small standalone reproducer containing those functions, constants, inputs and expected outputs. Remove the unavailable path assumptions. Retain the explicit disclosure that compiled Suite/WASM results have not been tested. Remove every `OWNER` placeholder before filing.

6. **Should-fix — The Cd concern is valid, but some wording implies guaranteed overstatement or sounds corrective toward the maintainer.**

   **Location:** `draft:74–76`.

   > “UMP Chapter 22 (p. 20) says the opposite way round…”

   **Neutral rewrite:**

   > “UMP Chapter 22 uses ‘conservative’ in the sense of avoiding overstated savings and therefore requires an orifice correction factor.”

   > “Cd = 1.0 … used for savings claims it overstates savings.”

   This is too categorical. Cd=1 is an idealized upper-bound assumption; whether a particular estimate overstates actual savings also depends on the actual geometry and other inputs.

   **Evidence:** `M/include/compressedAir/leak_survey/orifice_method.h:233–234` says “`a conservative upper bound`.” U, PDF 30:954, says correction factors “`must be applied … to ensure estimates are conservative`.”

   **Neutral rewrite:**

   > “Cd=1.0 gives an idealized upper-bound flow estimate. For leak-repair savings, this can produce a higher estimate than an appropriate geometry correction; please clarify the intended meaning of ‘conservative’.”

   The overall issue is courteous. These are wording refinements, not evidence of hostile tone.

7. **Minor — The Data Safety statement inaccurately says every input comes from a published example.**

   **Location:** `draft:144`.

   > “All inputs above are from the published examples.”

   Case (a), the temperature sweep and the all-cell comparisons are constructed scenarios.

   **Evidence:** E’s published case inputs differ from case (a), as shown in B1; `issue/measur_issue_numbers.py:84` explicitly constructs the temperature sweep.

   **Fix:**

   > “The inputs are published example values or synthetic scenarios; no customer or private operational data are included.”

8. **Minor — The template is followed sensibly, but the issue can be shorter and its acceptance criteria more actionable.**

   **Location:** `draft:42–165`; `M/ISSUE_TEMPLATE_suite-api-change.md:9–55`.

   All eight requested headings are present. “No applicable classification” and “Not applicable” for API/package changes are reasonable for documentation and tests. The template contains no documentation/test checkbox.

   The acceptance criterion “within the rounding of the printed values” does not fit synthetic case (a), and does not specify how a Suite-only test handles case (b)’s external adjustment.

   **Evidence:** Template:37–41 requests calculation expectations, coverage and verification. Draft:127–128 supplies general targets but no distinction between library and Desktop assertions.

   **Fix:** Specify:

   - Equation-derived flow check with an explicit tolerance for rounded constants.
   - Suite electricity expectation **45,240 kWh**.
   - Separate adjusted-savings expectation **43,882.8 kWh**.
   - Tip Sheet estimate-method line-item checks.

   For brevity, cut the #401 reference, the speculative midpoint explanation for 0.48/0.68, and most discussion of inconsistencies in the source publications. Keep the three documentation requests, concise supporting references, and one reproducible numerical example for each relevant path.

## Checks completed and found correct

- **Equation and constant audit:** The following checked expressions/constants match the supplied source text, except for the explicit deviations and unavailable visual evidence above.

  | Implementation | Source evidence checked |
  |---|---|
  | Essentials choking threshold, free-air-flow structure, +460 conversion | E, PDF 206:6803: “`ratio … less than 0.5283`”; 6805–6810 contains the flow expression and `(Ti + 460)` / line-temperature denominator. |
  | Essentials constants | E, PDF 207:6825–6833: **14.7, 28.37, 60, Cd 0.8, 144**; 6846–6848: **k=1.4, C7=3.03×10⁻⁵**. |
  | Essentials staged compression power and efficiencies | E, PDF 207:6837–6842 contains the staged pressure-ratio expression and “`Ea × Em`”; 6850–6856 and PDF 208:6869 give all eight implemented efficiencies: **0.88, 0.75, 0.82, 0.72, 0.80, 0.70, 0.70, 0.62**. |
  | Essentials annual energy and NBS table | E, PDF 209:6881: “`ES = L× H ×C8`”; 6884 gives **0.002545**. All five NBS rows match E, PDF 200:6627–6631, including units **ft³/year** and **kWh/h**. |
  | Workbook mass flow | W, PDF 82:2396: “`m = 1915.2 x k x A x P x (T + 460)-0.5`”; PDF 83:2408–2413 defines lbm/h, **k=0.65**, in², psia and °F. |
  | Workbook compression energy and annual cost/energy | W, PDF 83:2420–2430 supplies **0.0687, efficiency 0.65, ln(p2/p1), +460, 0.0002931**; PDF 84:2442–2446 supplies **P×L×HR×LF×CF**, with example **LF=0.6**. |
  | Tip Sheet table, factors and energy/cost expressions | All **30 cells** match T, PDF 1:70–74; line 76 supplies **0.97/0.61**. PDF 2:88–94 supplies **0.18 kW/cfm** and the annual-cost product. |
  | UMP leak-down equation | U, PDF 27:841: “`[(V × ΔP)/(Time × Palt)] × 1.25`”; definitions at 845–855 match the implemented units and multiplier. |
  | UMP savings and CCAF table | U, PDF 28:881: “`repaired leak volume × kWFL/CFMrated × Hours × CCAF`.” All **11 implemented CCAF entries** match PDF 29:913–923. Table 6 numerically matches the Tip Sheet table; U attributes it to DOE 2013. |
  | Moss equation and rule of thumb | S04, PDF 8:303–311 supplies **0.5303, πD²/4, 530, 0.07494, 60, C=0.61** and printed **3.96 scfm**; PDF 9:360–369 supplies **C=0.9**. PDF 8:320 supplies **4.2, 0.75 and 90%**. |
  | Linear model, inverse and savings difference | S05, PDF 4:120: “`FP = FP0 + (1 – FP0) FC`”; 124–126 defines normalized variables. S04, PDF 4:143 gives the inverse; PDF 5:179–184 gives after-power, power difference and annual savings. The `(1−FP0)` savings factor follows algebraically. |

- **Every example target was checked.** Apart from UMP-2’s derived target and the page errors already identified, these are the values actually printed:

  | Test IDs | Printed targets | Source location |
  |---|---|---|
  | ESS-1; ESS-2/2b; ESS-3; ESS-4; ESS-5 | 29.0; 6.9; 149.7; 408.0; 2,103 | E, PDF 205:6742,6764 |
  | WB-1/1b; WB-2; WB-3; WB-4; WB-5 | 303; 4.75; 124.3; 0.03643; 914 | W, PDF 83:2415–2430; PDF 84:2446 |
  | TS-1–4 | 5,611; 10,991; 38,776; 57,069 | T, PDF 2:94–96 |
  | UMP-1 | 43,883 | U, PDF 29:938 |
  | SK04-1; SK04-2; SK04-3/3b | 3.96; 102; 3,945 | S04, PDF 8:311,320; PDF 9:369 |
  | SK04-4/4b; SK04-5; SK04-6; SK04-7 | 2.8; 6.2; 2,000; 1,072 | S04, PDF 9:339,352; PDF 6:229; PDF 8:297 |
  | SK05-1; SK05-2; SK05-3/3b; SK05-4; SK05-5 | 65.5%; 12,000; 28,000; 42,000; 55,555 | S05, PDF 5:160,173; PDF 6:213,215,219 |

- **Every numbered code link in the English issue points to the described text or operation.**

  | Draft line | Supplied file:line | Checked evidence |
  |---:|---|---|
  | 46 | `M/include/compressedAir/compressed_air_utils.h:8–12` | Says adjustment is divided by 100 and applied to specific power. |
  | 47 | `M/src/treasureHunt/compressed_air_reduction.cpp:48–49` | Actually applies that percentage. |
  | 48 | `M/src/compressedAir/leak_survey/compressed_air_leak_survey.cpp:42–45` | Electricity uses specific power without reading adjustment. |
  | 49 | `D/air-leak-survey.service.ts:169–172` | Applies adjustment to savings afterwards. |
  | 57 | `M/src/compressedAir/leak_survey/orifice_method.cpp:15–17` | Reference density uses entered temperature. |
  | 58 | `M/docs/dox-content/calculators/compressedAir/leak_survey/orifice_method_calculator.dox:149–152` | Explicitly says same temperature as supply density. |
  | 59 | Same `.dox`:245–249 | Claims a common reference state across temperatures. |
  | 68 | `M/include/compressedAir/leak_survey/orifice_method.h:72` | Says “standard (atmospheric) conditions.” |
  | 74 | Same header:229–234; `.dox`:21–22 | Contains the quoted “conservative upper bound” wording. |
  | 94 | `M/tests/cpp/compressedAir/leak_survey/orifice_method.unit.cpp:8–9` | Identifies the regression reference and 550°F input. |

  Also verified: **nine bibliography entries**, none specifically about compressed air; Desktop help’s **200–300°F** statement at `D/air-leak-survey-help.component.html:250–251`; “at the leak point” at `M/include/compressedAir/leak_survey/orifice_method.h:58`; the NREL link and listed CCAF percentages at Desktop help:337,355–396.

- **Issue numerical audit:** Fresh in-memory execution of the script’s calculation portion reproduced the stored JSON exactly after normal JSON key conversion. The English numerical tables round it correctly: **20.8455/20.8464**, **45,240/43,882.8**, the three dollar amounts, all five temperature flows and ratios, and the **1.8%–6.7% / 17.8%–23.5%** ranges. The midpoint arithmetic for **0.48/0.68** is correct; its historical provenance remains unverified.

- **Execution and generated-document checks:** On Python **3.11.9**, `python -B -m unittest discover -s tests` returned:

  ```text
  Ran 44 tests in 0.002s

  OK
  ```

  I did **not** execute `python tools/mutation_check.py` as written: it creates modified temporary copies and overwrites `tools/mutation_log.txt`. A read-only, in-memory replay caught **13/13 mutations**, with the same failure counts as the supplied log and no test errors. Both generated Markdown documents exactly match the generator’s current in-memory output.