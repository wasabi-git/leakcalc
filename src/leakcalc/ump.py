"""Uniform Methods Project (UMP) Chapter 22 method.

Source
------
Benton, N., Burns, P., & Zahlan, J. (2021). *Chapter 22: Compressed Air Evaluation
Protocol. The Uniform Methods Project: Methods for Determining Energy Efficiency
Savings for Specific Measures*. National Renewable Energy Laboratory,
NREL/SR-7A40-77820. Section 3.2:

* leak-down test, Equation 11: printed p. 17 (PDF p. 27);
* simplified savings, Equation 12, and its conditions: printed p. 18 (PDF p. 28);
* Table 5 (CCAF) and the worked example: printed p. 19 (PDF p. 29);
* Table 6 (leakage rates, reprinted from DOE Tip Sheet #3): printed p. 20 (PDF p. 30).

Equation 12 applies only when one trim compressor carries the variable load, the
number of running compressors does not change, and the system "is well-controlled and
operates predictably" (p. 18); otherwise UMP requires the CFM-bin method, which is not
implemented here. Each CCAF in Table 5 is the slope of the part-load power curve
between 40 % and 80 % capacity (p. 19).
"""

from . import tipsheet

# Table 5, p. 19. Centrifugal compressors: "Varies" (see footnote a); not included.
CCAF = {
    "reciprocating_on_off": 1.00,
    "reciprocating_load_unload": 0.74,
    "screw_load_unload_oil_free": 0.73,
    "screw_load_unload_1gal_per_cfm": 0.43,
    "screw_load_unload_3gal_per_cfm": 0.53,
    "screw_load_unload_5gal_per_cfm": 0.63,
    "screw_load_unload_10gal_per_cfm": 0.73,
    "screw_inlet_modulation": 0.30,
    "screw_inlet_modulation_with_unloading": 0.30,
    "screw_variable_displacement": 0.60,
    "screw_variable_speed": 0.97,
}

LEAKDOWN_MULTIPLIER = 1.25   # p. 17


def leakdown_scfm(volume_ft3, pressure_drop_psi, minutes, p_alt_psia=14.7):
    """Equation 11 (p. 17): Leak flow SCFM = [(V x dP) / (Time x Palt)] x 1.25.

    The 1.25 corrects to normal system pressure when the test runs down to about half
    the starting pressure."""
    return volume_ft3 * pressure_drop_psi / (minutes * p_alt_psia) * LEAKDOWN_MULTIPLIER


def annual_energy_kwh(leak_scfm, kw_full_load, cfm_rated, hours, ccaf):
    """Equation 12 (p. 18): kWh saved = repaired leak volume x kW_FL / CFM_rated x Hours x CCAF.

    ``ccaf`` is a number or a key of :data:`CCAF`."""
    if isinstance(ccaf, str):
        ccaf = CCAF[ccaf]
    return leak_scfm * kw_full_load / cfm_rated * hours * ccaf


def table6_cfm(diameter_in, psig, orifice="sharp"):
    """Table 6 (p. 20) is the DOE Tip Sheet #3 table; UMP says the 0.97 / 0.61 factors
    "must be applied" so that estimates are conservative."""
    if orifice == "table":
        raise ValueError("UMP requires an orifice correction factor ('sharp' or 'rounded')")
    return tipsheet.leakage_cfm(diameter_in, psig, orifice)
