"""Evaluate one leak with a selection of the implemented methods.

The reference case used in docs/algorithm_comparison.md is a 1/8-inch hole at
100 psig that leaks all year (8,760 h). Each method is run with its own published
defaults. Where a method needs an input that the leak itself does not fix
(temperatures, compressor and motor efficiency), the shared values in
:data:`REFERENCE` are used and listed in the output. The rows still differ in orifice factor, load
factor, compressor and control type and compression model, so this is a scenario
comparison of published assumptions, not a controlled test of the equations alone.
The leak-down test (UMP Eq. 11) is not included: it needs a measured pressure decay.
"""

from fractions import Fraction

from . import essentials, schmidt, tipsheet, ump, workbook
from .units import PSIA_STD_ATM

REFERENCE = {
    "diameter_in": 1 / 8,
    "line_psig": 100,
    "hours": 8760,
    "air_temp_f": 70.0,          # inlet and line; the Moss equation fixes 530 R = 70 F
    "motor_eff": 0.90,           # Schmidt & Kissock rule-of-thumb value
    "compressor": "rotary_screw",  # Essentials adiabatic efficiency 0.82, single stage
    "kw_per_cfm": 0.18,          # Tip Sheet #3; also used for UMP so that only CCAF differs
}
STD_DENSITY = schmidt.MOSS_DENSITY   # lbm/ft3, to express mass flow as scfm


def run(ref=None):
    """Return a list of result rows (dicts) for the reference leak."""
    r = dict(REFERENCE if ref is None else ref)
    d, psig, h, t = r["diameter_in"], r["line_psig"], r["hours"], r["air_temp_f"]
    psia = psig + PSIA_STD_ATM
    rows = []

    def add(group, method, source, flow_scfm, kwh, assumptions):
        rows.append({"group": group, "method": method, "source": source, "flow_scfm": flow_scfm,
                     "kwh_per_year": kwh, "assumptions": assumptions})

    # 1. Essentials v3: choked flow + adiabatic power
    ea = essentials.ADIABATIC_EFFICIENCY[r["compressor"]]
    es = essentials.leak_savings(d, psig, h, t, t, ea, r["motor_eff"])
    add("core", "Essentials v3 formula", "Essentials v3, pp. 195-198", es["flow_cfm"], es["energy_kwh"],
        f"Cd 0.8; Ti = Tl = {t:g} F; screw Ea {ea}; motor {r['motor_eff']}; 1 stage")
    # 1b. Essentials Table 6.3 (NBS), 100 psi only
    if psig == 100 and d in essentials.NBS_TABLE_100PSI:
        ft3_yr, kwh_h = essentials.NBS_TABLE_100PSI[d]
        add("core", "Essentials v3 Table 6.3 (NBS)", "Essentials v3, p. 189", ft3_yr / 8760 / 60,
            essentials.nbs_table_kwh(d, h), "table value 3.4 kWh per hour of leaking; flow = ft3/yr / 525,600 min")

    # 2. Self-Assessment Workbook: Fliegner + isothermal
    for lf, tag in ((1.0, "load factor 1.0"), (workbook.PARTIAL_LOAD_FACTOR, "load factor 0.6 (as in the worked example)")):
        wb = workbook.leak_savings(d, psig, h, t, t, load_factor=lf)
        add("core", f"Workbook Fliegner, {tag}", "Workbook v2.0, pp. 77-79", wb["mass_flow_lbm_hr"] / 60 / STD_DENSITY,
            wb["energy_kwh"], f"k 0.65; T = {t:g} F; isothermal, eta 0.65; LF {lf}")

    # 3. Tip Sheet #3: table x factor x 0.18 kW/cfm
    if tipsheet.has_cell(d, psig):
        for orf in ("sharp", "rounded", "table"):
            q = tipsheet.leakage_cfm(d, psig, orf)
            # The Tip Sheet says the table values "should be multiplied" by 0.97 or 0.61, so the
            # uncorrected value is shown for reference only and is not one of the published choices.
            add("core" if orf != "table" else "reference", f"Tip Sheet #3 table, {orf}" + (" (no factor)" if orf == "table" else f" x {tipsheet.ORIFICE_FACTOR[orf]}"),
                "Tip Sheet #3, pp. 1-2", q, tipsheet.annual_energy_kwh(q, h, r["kw_per_cfm"]),
                f"{r['kw_per_cfm']} kW/cfm")

    # 4. Schmidt & Kissock: Moss equation + rule of thumb
    q_moss = schmidt.moss_scfm(d, psia)
    add("core", "Schmidt & Kissock Moss + rule of thumb", "S2004 Eq. 16, PDF p. 8", q_moss,
        schmidt.rule_of_thumb_kw(q_moss) * h, "C 0.61; 4.2 cfm/bhp; 0.75 kW/hp; motor 0.90")

    # 5. Control-mode corrections
    if tipsheet.has_cell(d, psig):
        q_ump = ump.table6_cfm(d, psig, "sharp")
        for key in ("reciprocating_on_off", "screw_variable_speed", "reciprocating_load_unload",
                    "screw_load_unload_10gal_per_cfm", "screw_load_unload_5gal_per_cfm",
                    "screw_variable_displacement", "screw_load_unload_3gal_per_cfm",
                    "screw_load_unload_1gal_per_cfm", "screw_inlet_modulation"):
            add("control", f"UMP Eq. 12, CCAF {ump.CCAF[key]:.2f} ({key})", "UMP Ch. 22, pp. 18-20", q_ump,
                ump.annual_energy_kwh(q_ump, r["kw_per_cfm"], 1.0, h, key),
                f"Table 6 x 0.61; kW_FL/CFM_rated {r['kw_per_cfm']}")
    for key, fp0 in schmidt.FP0_FIGURE2.items():
        add("control", f"Schmidt & Kissock, (1 - FP0) with FP0 {fp0:.2f} ({key})", "S2005 Fig. 2 and Eq. 1", q_moss,
            schmidt.control_corrected_kw(q_moss, fp0) * h, "Moss C 0.61; rule-of-thumb sizing x (1 - FP0)")
    return rows


def spread(rows, group=None):
    """Max / min of kWh over the rows (optionally one group)."""
    vals = [x["kwh_per_year"] for x in rows if group is None or x["group"] == group]
    return max(vals) / min(vals), min(vals), max(vals)
