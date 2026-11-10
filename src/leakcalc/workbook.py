"""Self-Assessment Workbook method: Fliegner's formula and isothermal compression.

Source
------
Muller, M. R., & Papadaratsakis, K. (2003). *Self-Assessment Workbook for Small
Manufacturers*, Version 2.0. Center for Advanced Energy Systems, Rutgers University,
for the U.S. DOE Office of Energy Efficiency and Renewable Energy.
Section 4.15 "Repair Compressed Air Leaks", printed pp. 77-79 (PDF pp. 82-84).

* mass flow (Fliegner's formula) and worked example: printed pp. 77-78;
* isothermal compression energy: printed p. 78;
* annual cost: printed pp. 78-79.
"""

import math

from .units import PSIA_STD_ATM, f_to_rankine, hole_area_in2

FLIEGNER_CONSTANT = 1915.2       # lbm/hr per (in2 * psia / R^0.5); p. 77
NOZZLE_COEFF = 0.65              # p. 78 ("usually between 0.6 and 0.7", footnote 32)
GAS_CONSTANT_BTU = 0.0687        # Btu/(lbm*R); p. 78
COMPRESSOR_EFF = 0.65            # p. 78
KWH_PER_BTU = 0.0002931          # p. 78
PARTIAL_LOAD_FACTOR = 0.6        # "average partial load factor (estimated here to be 0.6)", p. 79


def mass_flow_lbm_hr(diameter_in, line_psia, line_temp_f, k=NOZZLE_COEFF, area_in2=None):
    """Fliegner's formula, lbm/hr (p. 77):  m = 1915.2 * k * A * P * (T + 460)^-0.5.

    ``line_psia`` is ABSOLUTE line pressure. ``area_in2`` overrides the area computed
    from ``diameter_in`` (the worked example rounds the area to 0.04909 and 0.00077 in2).
    """
    a = hole_area_in2(diameter_in) if area_in2 is None else area_in2
    return FLIEGNER_CONSTANT * k * a * line_psia / math.sqrt(f_to_rankine(line_temp_f))


def compression_energy_btu_per_lbm(inlet_temp_f, p1_psia, p2_psia, eff=COMPRESSOR_EFF):
    """Isothermal compression energy, Btu/lbm (p. 78):  PR = 0.0687 * (1/eta) * (T1 + 460) * ln(p2/p1)."""
    return GAS_CONSTANT_BTU / eff * f_to_rankine(inlet_temp_f) * math.log(p2_psia / p1_psia)


def compression_energy_kwh_per_lbm(inlet_temp_f, p1_psia, p2_psia, eff=COMPRESSOR_EFF):
    return compression_energy_btu_per_lbm(inlet_temp_f, p1_psia, p2_psia, eff) * KWH_PER_BTU


def annual_energy_kwh(kwh_per_lbm, leak_lbm_hr, hours, load_factor=PARTIAL_LOAD_FACTOR):
    """Annual energy, kWh/yr: P * L * HR * LF (the cost equation on p. 78-79 without the $/kWh)."""
    return kwh_per_lbm * leak_lbm_hr * hours * load_factor


def leak_savings(diameter_in, line_psig, hours, line_temp_f, inlet_temp_f, discharge_psig=None,
                 k=NOZZLE_COEFF, eff=COMPRESSOR_EFF, load_factor=PARTIAL_LOAD_FACTOR, atm_psia=PSIA_STD_ATM):
    """Convenience wrapper. ``discharge_psig`` defaults to the line pressure."""
    if discharge_psig is None:
        discharge_psig = line_psig
    m = mass_flow_lbm_hr(diameter_in, line_psig + atm_psia, line_temp_f, k)
    e = compression_energy_kwh_per_lbm(inlet_temp_f, atm_psia, discharge_psig + atm_psia, eff)
    return {"mass_flow_lbm_hr": m, "kwh_per_lbm": e,
            "energy_kwh": annual_energy_kwh(e, m, hours, load_factor)}
