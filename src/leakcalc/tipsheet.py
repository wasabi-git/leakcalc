"""DOE Compressed Air Tip Sheet #3 method: leakage-rate table x specific power.

Source
------
U.S. Department of Energy, Industrial Technologies Program (2004). *Minimize
Compressed Air Leaks*. Compressed Air Tip Sheet #3, DOE/GO-102004-1964, revised
August 2004. 2 pp.

* leakage-rate table and orifice correction factors: p. 1;
* worked example (cost equation, 0.18 kW per cfm, sharp-orifice factor 0.61): pp. 1-2.

The same table is reprinted as Table 6 of UMP Chapter 22 (see :mod:`leakcalc.ump`),
which writes 23.1 where the Tip Sheet writes 23.10.
"""

from fractions import Fraction

# Leakage rates (cfm), p. 1. Keys: psig -> {orifice diameter (in) -> cfm}
DIAMETERS = (Fraction(1, 64), Fraction(1, 32), Fraction(1, 16), Fraction(1, 8), Fraction(1, 4), Fraction(3, 8))
_ROWS = {
    70: (0.29, 1.16, 4.66, 18.62, 74.4, 167.8),
    80: (0.32, 1.26, 5.24, 20.76, 83.1, 187.2),
    90: (0.36, 1.46, 5.72, 23.10, 92.0, 206.6),
    100: (0.40, 1.55, 6.31, 25.22, 100.9, 227.0),
    125: (0.48, 1.94, 7.66, 30.65, 122.2, 275.5),
}
LEAKAGE_CFM = {p: dict(zip(DIAMETERS, row)) for p, row in _ROWS.items()}

ORIFICE_FACTOR = {"table": 1.0, "rounded": 0.97, "sharp": 0.61}   # p. 1, table footnote a
KW_PER_CFM = 0.18      # "approximately 18 kilowatts (kW)/100 cfm", p. 2


def table_column(diameter_in):
    """The table column for ``diameter_in``, or None. A diameter matches a column only if it
    equals it to within 1e-9 in (so 1/8 and 0.125 match, 0.124 does not)."""
    for d in DIAMETERS:
        if abs(float(diameter_in) - float(d)) <= 1e-9:
            return d
    return None


def has_cell(diameter_in, psig):
    return psig in LEAKAGE_CFM and table_column(diameter_in) is not None


def leakage_cfm(diameter_in, psig, orifice="sharp"):
    """Table value x orifice factor. Only the tabulated pressures and diameters are allowed
    (no interpolation: the source gives none)."""
    if psig not in LEAKAGE_CFM:
        raise KeyError(f"no table row for {psig} psig; rows: {sorted(LEAKAGE_CFM)}")
    d = table_column(diameter_in)
    if d is None:
        raise KeyError(f"no table column for {diameter_in} in; columns: {[str(x) for x in DIAMETERS]}")
    return LEAKAGE_CFM[psig][d] * ORIFICE_FACTOR[orifice]


def annual_energy_kwh(cfm, hours, kw_per_cfm=KW_PER_CFM, n_leaks=1):
    """# of leaks x leakage rate (cfm) x kW/cfm x # of hours (p. 2, without the $/kWh)."""
    return n_leaks * cfm * kw_per_cfm * hours


def annual_cost(n_leaks, table_cfm, orifice_factor, kw_per_cfm, hours, usd_per_kwh):
    """Cost savings exactly as written on p. 2:
    # of leaks x leakage rate (cfm) x kW/cfm x # of hours x $/kWh, with the orifice factor
    multiplied in as in the worked example."""
    return n_leaks * table_cfm * orifice_factor * kw_per_cfm * hours * usd_per_kwh
