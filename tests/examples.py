"""Worked examples printed in the official sources, as test data.

Each entry gives the value printed in the source, a function that recomputes it with
leakcalc, a relative tolerance that reflects the rounding of the printed value, and
whether the recomputation is EXPECTED to match. Where a printed value cannot be
reproduced from the source's own equation, the entry says so (``match=False``) and
the test checks that the mismatch is real; the equation is never adjusted to force
agreement. docs/worked_examples.md is generated from this list.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from leakcalc import essentials as E  # noqa: E402
from leakcalc import schmidt as S  # noqa: E402
from leakcalc import tipsheet as T  # noqa: E402
from leakcalc import ump as U  # noqa: E402
from leakcalc import workbook as W  # noqa: E402

# Essentials v3 case study inputs, printed p. 192 (PDF p. 203)
ESS = dict(inlet_temp_f=92, line_temp_f=72, line_psig=115, motor_eff=0.915, adiabatic_eff=0.82, hours=8520)
ESS_TABLE = {  # printed p. 194 (PDF p. 205): diameter -> (cfm, hp, MMBtu/yr, $/yr)
    1 / 64: (0.5, 0.1, 0.2, 31), 1 / 32: (1.8, 0.4, 8.7, 122), 1 / 16: (7.2, 1.7, 36.9, 518),
    1 / 8: (29.0, 6.9, 149.7, 2103), 3 / 16: (65.2, 15.4, 334.1, 4694), 1 / 4: (115.8, 27.4, 594.4, 8351),
    3 / 8: (260.6, 61.7, 1334.8, 18805),
}


def ess_flow(d):
    return E.free_air_flow_cfm(d, ESS["line_psig"], ESS["inlet_temp_f"], ESS["line_temp_f"])


def ess_hp_from_printed_flow(d, motor=True):
    em = ESS["motor_eff"] if motor else 1.0
    return E.power_loss_hp(ESS_TABLE[d][0], ESS["line_psig"], ESS["adiabatic_eff"], em)


EXAMPLES = [
    # ---------------------------------------------------------------- Essentials v3
    dict(id="ESS-1", source="Essentials v3", page="pp. 192-195 (PDF 203-206)",
         what="Flow through a 1/8-in leak, 115 psig, Ti 92 F, Tl 72 F, Cd 0.8 (cfm)",
         printed=29.0, value=lambda: ess_flow(1 / 8), rtol=0.01, match=False, computed=24.505,
         note="The printed flow equation gives 24.50 cfm; the printed table is 1.18 times higher. "
              "The ratio is 1.175-1.183 for every diameter from 1/32 to 3/8 in (1/64 in: 1.31, printed to one decimal), so the table and the printed "
              "equation do not agree. The source does not say why; a different constant or input, or an "
              "arithmetic or transcription error, are all possible."),
    dict(id="ESS-2", source="Essentials v3", page="pp. 194-196 (PDF 205-207)",
         what="Power loss for the printed 29.0 cfm, screw Ea 0.82, motor 0.915, 1 stage (hp)",
         printed=6.9, value=lambda: ess_hp_from_printed_flow(1 / 8), rtol=0.01, match=False, computed=7.4867,
         note="The printed power equation (divide by Ea x Em) gives 7.49 hp. Dividing by Ea only gives "
              "6.85 hp, which rounds to the printed 6.9: the table appears to omit the motor efficiency."),
    dict(id="ESS-2b", source="Essentials v3", page="pp. 194-196 (PDF 205-207)",
         what="Same as ESS-2 but without motor efficiency (hp) - diagnostic, not the printed equation",
         printed=6.9, value=lambda: ess_hp_from_printed_flow(1 / 8, motor=False), rtol=0.01, match=True,
         note="Supports the explanation in ESS-2."),
    dict(id="ESS-3", source="Essentials v3", page="pp. 194, 198 (PDF 205, 209)",
         what="Annual energy for the printed 6.9 hp x 8,520 h x 0.002545 (MMBtu/yr)",
         printed=149.7, value=lambda: E.annual_energy_mmbtu(6.9, 8520), rtol=0.005, match=True,
         note="Reproduced within the rounding of 6.9 hp (149.6 vs 149.7)."),
    dict(id="ESS-4", source="Essentials v3", page="p. 194 (PDF 205)",
         what="Total energy savings, seven 1/16-in leaks and one 1/8-in leak (MMBtu/yr)",
         printed=408.0, value=lambda: 7 * ESS_TABLE[1 / 16][2] + ESS_TABLE[1 / 8][2], rtol=0.0005, match=True,
         note="Arithmetic of the summary table."),
    dict(id="ESS-5", source="Essentials v3", page="pp. 192, 194 (PDF 203, 205)",
         what="Cost of the 1/8-in leak at $14.05/MMBtu ($/yr)",
         printed=2103, value=lambda: ESS_TABLE[1 / 8][2] * 14.05, rtol=0.001, match=True, note=""),
    # ---------------------------------------------------------------- Self-Assessment Workbook
    dict(id="WB-1", source="Self-Assessment Workbook v2.0", page="p. 78 (PDF 83)",
         what="Fliegner flow, 1/4-in hole (A = 0.04909 in2), 114.7 psia, 75 F, k 0.65 (lbm/hr)",
         printed=303, value=lambda: W.mass_flow_lbm_hr(0.25, 114.7, 75, area_in2=0.04909), rtol=0.002, match=True,
         note="Reproduced. Note that the text states a line pressure of 110 psi (124.7 psia) but the "
              "calculation uses 114.7 psia; see WB-1b."),
    dict(id="WB-1b", source="Self-Assessment Workbook v2.0", page="p. 78 (PDF 83)",
         what="Same leak at the stated 110 psig = 124.7 psia (lbm/hr)",
         printed=303, value=lambda: W.mass_flow_lbm_hr(0.25, 110 + 14.7, 75, area_in2=0.04909), rtol=0.01, match=False, computed=329.47,
         note="Gives 329.5 lbm/hr. The printed 303 corresponds to 114.7 psia, i.e. 100 psig, not the 110 psi "
              "stated in the text and used for the compression energy (WB-3)."),
    dict(id="WB-2", source="Self-Assessment Workbook v2.0", page="p. 78 (PDF 83)",
         what="Fliegner flow, 1/32-in hole (A = 0.00077 in2), 114.7 psia, 75 F (lbm/hr)",
         printed=4.75, value=lambda: W.mass_flow_lbm_hr(1 / 32, 114.7, 75, area_in2=0.00077), rtol=0.002, match=True,
         note="With the exact area (0.000767 in2) the flow is 4.73 lbm/hr."),
    dict(id="WB-3", source="Self-Assessment Workbook v2.0", page="p. 78 (PDF 83)",
         what="Isothermal compression energy, eta 0.65, T1 90 F, 14.7 -> 124.7 psia (Btu/lbm)",
         printed=124.3, value=lambda: W.compression_energy_btu_per_lbm(90, 14.7, 124.7), rtol=0.0005, match=True,
         note="Follows the numerical substitution, which uses 90 F; the preceding prose says the intake air is "
              "assumed to average 95 F."),
    dict(id="WB-4", source="Self-Assessment Workbook v2.0", page="p. 78 (PDF 83)",
         what="Same in kWh/lbm (x 0.0002931)", printed=0.03643,
         value=lambda: W.compression_energy_kwh_per_lbm(90, 14.7, 124.7), rtol=0.0005, match=True,
         note="Same 90 F substitution as WB-3 (prose: 95 F)."),
    dict(id="WB-5", source="Self-Assessment Workbook v2.0", page="pp. 78-79 (PDF 83-84)",
         what="Cost savings: 0.03643 kWh/lbm x 317.25 lbm/hr x 2,080 h x LF 0.6 x $0.0634/kWh ($/yr)",
         printed=914, value=lambda: W.annual_energy_kwh(0.03643, 317.25, 2080, 0.6) * 0.0634, rtol=0.001, match=True,
         note="Note the text says 'one significant air leak' and three small ones; the total 317.25 = 303 + 3 x 4.75."),
    # ---------------------------------------------------------------- Tip Sheet #3
    dict(id="TS-1", source="DOE Tip Sheet #3", page="p. 2",
         what="100 leaks of 1/32 in at 90 psig, sharp (x 0.61), 0.18 kW/cfm, 7,000 h, $0.05/kWh ($/yr)",
         printed=5611, value=lambda: T.annual_cost(100, T.LEAKAGE_CFM[90][T.DIAMETERS[1]], 0.61, 0.18, 7000, 0.05),
         rtol=0.0005, match=True, note=""),
    dict(id="TS-2", source="DOE Tip Sheet #3", page="p. 2",
         what="50 leaks of 1/16 in at 90 psig ($/yr)", printed=10991,
         value=lambda: T.annual_cost(50, T.LEAKAGE_CFM[90][T.DIAMETERS[2]], 0.61, 0.18, 7000, 0.05),
         rtol=0.0005, match=True, note=""),
    dict(id="TS-3", source="DOE Tip Sheet #3", page="p. 2",
         what="10 leaks of 1/4 in at 100 psig ($/yr)", printed=38776,
         value=lambda: T.annual_cost(10, T.LEAKAGE_CFM[100][T.DIAMETERS[4]], 0.61, 0.18, 7000, 0.05),
         rtol=0.0005, match=True, note=""),
    dict(id="TS-4", source="DOE Tip Sheet #3", page="p. 2",
         what="Total of the three lines ($/yr)", printed=57069,
         value=lambda: sum(T.annual_cost(n, T.LEAKAGE_CFM[p][T.DIAMETERS[i]], 0.61, 0.18, 7000, 0.05)
                           for n, p, i in ((100, 90, 1), (50, 90, 2), (10, 100, 4))),
         rtol=0.001, match=False, computed=55377.63,
         note="The three printed line items add up to $55,378, not the printed total $57,069 (3.1 % higher). "
              "The '1/4-in leaks are almost 70 %' remark is consistent with the correct sum (70.0 %) rather than the printed total (67.9 %)."),
    # ---------------------------------------------------------------- UMP Chapter 22
    dict(id="UMP-1", source="UMP Chapter 22", page="p. 19 (PDF 29)",
         what="58 scfm x 67.5 kW / 360 scfm x 4,160 h x CCAF 0.97 (kWh/yr)", printed=43883,
         value=lambda: U.annual_energy_kwh(58, 67.5, 360, 4160, "screw_variable_speed"), rtol=0.0001, match=True, note=""),
    dict(id="UMP-2", source="UMP Chapter 22", page="p. 20 (PDF 30)",
         what="Table 6 value, 1/8 in at 100 psig, before orifice correction (cfm)", printed=25.22,
         value=lambda: U.table6_cfm(1 / 8, 100, "sharp") / T.ORIFICE_FACTOR["sharp"], rtol=1e-9, match=True,
         note="Table 6 is the Tip Sheet #3 table; the 0.97 / 0.61 orifice factors are printed separately below it. UMP Equation 11 (leak-down test) has no worked example in the chapter, so it is checked against hand-calculated values in tests/test_behaviour.py instead."),
    # ---------------------------------------------------------------- Schmidt & Kissock 2004
    dict(id="SK04-1", source="Schmidt & Kissock 2004", page="PDF p. 8",
         what="Moss equation, 1/16 in, C 0.61, 100 psig (scfm)", printed=3.96,
         value=lambda: S.moss_scfm(1 / 16, 114.7, 0.61), rtol=0.002, match=True, note=""),
    dict(id="SK04-2", source="Schmidt & Kissock 2004", page="PDF p. 9",
         what="Moss equation, 1/4-in tube, C 0.9, 110 psig (scfm)", printed=102,
         value=lambda: S.moss_scfm(1 / 4, 124.7, 0.9), rtol=0.005, match=True, note="101.6 scfm."),
    dict(id="SK04-3", source="Schmidt & Kissock 2004", page="PDF p. 8",
         what="Rule of thumb, 70 cfm, 4.2 cfm/bhp, 0.75 kW/hp as printed, motor 90 %, 4,080 h, $0.07 ($/yr)",
         printed=3945, value=lambda: S.rule_of_thumb_kw(70) * 4080 * 0.07, rtol=0.001, match=False, computed=3966.67,
         note="With the printed 0.75 kW/hp the result is $3,967. With 0.746 kW/hp it is $3,945.51 (SK04-3b), approximately "
              "consistent with the printed $3,945; the paper does not say which conversion it used."),
    dict(id="SK04-3b", source="Schmidt & Kissock 2004", page="PDF p. 8",
         what="Same with 0.746 kW/hp ($/yr) - diagnostic", printed=3945,
         value=lambda: S.rule_of_thumb_kw(70, kw_per_hp=0.746) * 4080 * 0.07, rtol=0.001, match=True, note=""),
    dict(id="SK04-4", source="Schmidt & Kissock 2004", page="PDF pp. 8-9",
         what="Modulation, FP0 0.81, FC 0.47 -> 0.21: savings with the paper's rounded steps "
              "(47 kW - 52 kW x 85 %) (kW)", printed=2.8,
         value=lambda: 47 - 52 * round(S.fraction_power(0.21, 0.81), 2), rtol=0.01, match=True,
         note="Reproduced only by following the paper's rounding: measured 47 kW before, FP rounded to 85 % after."),
    dict(id="SK04-4b", source="Schmidt & Kissock 2004", page="PDF pp. 8-9",
         what="Same case with the linear model at full precision (FC 0.47, 70 of 265 cfm removed) (kW)",
         printed=2.8, value=lambda: S.demand_reduction_kw(52, 265, 0.81, 0.47, 70)["savings_kw"], rtol=0.02, match=False, computed=2.6098,
         note="The model gives 2.61 kW (7 % lower). Also, 47/52 and 42/52 at full precision give FC = 0.50, "
              "not the 0.47 obtained from the rounded 90 % and 81 %."),
    dict(id="SK04-5", source="Schmidt & Kissock 2004", page="PDF p. 9",
         what="Load/unload, FP0 0.55, 70 of 265 cfm removed, 52 kW full load (kW)", printed=6.2,
         value=lambda: S.demand_reduction_kw(52, 265, 0.55, 0.47, 70)["savings_kw"], rtol=0.01, match=True,
         note="6.18 kW at full precision; the paper's rounded steps (40 - 33.8) give the same 6.2."),
    dict(id="SK04-6", source="Schmidt & Kissock 2004", page="PDF p. 6",
         what="Control switch, modulation -> load/unload: 7 kW x 4,080 h x $0.07 ($/yr)", printed=2000,
         value=lambda: (47 - round(52 * round(S.fraction_power(0.47, 0.55), 2))) * 4080 * 0.07, rtol=0.001, match=True,
         note="Reproduced only with the paper's rounding: FP 76.15 % -> 76 %, 52 x 76 % = 39.5 kW -> 40 kW, "
              "7 kW x 4,080 x 0.07 = $1,999 -> '$2,000'. Without rounding the after-power is 39.6 kW and the "
              "saving 7.4 kW ($2,114)."),
    dict(id="SK04-7", source="Schmidt & Kissock 2004", page="PDF pp. 7-8",
         what="Leak load from logged power: FC = (0.71 - 0.11) / 0.89 x 1,600 cfm (cfm)", printed=1072,
         value=lambda: round(S.fraction_capacity(0.71, 0.11), 2) * 1600, rtol=0.0005, match=True,
         note="Reproduced with FC rounded to 67 %. The text gives no-load power as 23 kW but divides 22 kW by 200 kW; "
              "with 23 kW, FC = 67.2 % and 1,076 cfm."),
    # ---------------------------------------------------------------- Schmidt & Kissock 2005
    dict(id="SK05-1", source="Schmidt & Kissock 2005", page="p. 1-135",
         what="Control switch: FP 0.90, FP0 0.71 -> FC (fraction)", printed=0.655,
         value=lambda: S.fraction_capacity(0.90, 0.71), rtol=0.002, match=True,
         note="The printed expression divides by 0.19, but 0.655 is (0.90 - 0.71) / 0.29; the printed "
              "denominator is a typo and the result follows Eq. 1."),
    dict(id="SK05-2", source="Schmidt & Kissock 2005", page="p. 1-135",
         what="Control switch: 47 kW - 52 kW x FP(0.655, FP0 0.55), x 4,000 h (kWh/yr)", printed=12000,
         value=lambda: round(47 - 52 * S.fraction_power(0.655, 0.55)) * 4000, rtol=0.001, match=True,
         note="Uses the paper's rounding of the savings to 3 kW; unrounded it is 3.07 kW and 12,276 kWh/yr."),
    dict(id="SK05-3", source="Schmidt & Kissock 2005", page="p. 1-136",
         what="Demand cut of 70 scfm in modulation, consistent model (FP0 0.71, FC 0.655 before) (kWh/yr)",
         printed=28000, value=lambda: S.demand_reduction_kw(52, 265, 0.71, 0.655, 70)["savings_kw"] * 4000,
         rtol=0.02, match=False, computed=15933.6,
         note="The consistent model gives 15,934 kWh/yr. The paper takes the 'before' power as the measured 47 kW "
              "(FC 65.5 %) but computes the 'after' state from FC 47 % (125 - 70 = 55 cfm), which mixes two "
              "baselines; see SK05-3b."),
    dict(id="SK05-3b", source="Schmidt & Kissock 2005", page="p. 1-136",
         what="Same, following the paper's steps: (47 kW - 52 kW x 77 %) x 4,000 h (kWh/yr)", printed=28000,
         value=lambda: round(47 - 52 * round(S.fraction_power(55 / 265, 0.71), 2)) * 4000, rtol=0.001, match=True, note=""),
    dict(id="SK05-4", source="Schmidt & Kissock 2005", page="p. 1-136",
         what="Demand cut of 70 scfm in load/unload (FP0 0.55), consistent model (kWh/yr)", printed=42000,
         value=lambda: S.demand_reduction_kw(52, 265, 0.55, 0.655, 70)["savings_kw"] * 4000, rtol=0.02, match=False, computed=24724.5,
         note="The consistent model gives 24,725 kWh/yr. A possible reconstruction (the paper shows no intermediate step): 42,000 is reproduced by 44 kW (load/unload at "
              "FC 65.5 %) minus 33.5 kW (load/unload at FC 21 %) = 10.5 kW x 4,000 h, again mixing two baselines."),
    dict(id="SK05-5", source="Schmidt & Kissock 2005", page="p. 1-136",
         what="Rule of thumb, 70 cfm, 0.75 kW/hp, motor 90 %, 4,000 h (kWh/yr)", printed=55555,
         value=lambda: S.rule_of_thumb_kw(70) * 4000, rtol=0.0001, match=True, note=""),
]


def within(value, printed, rtol):
    return math.isclose(value, printed, rel_tol=rtol)
