"""Unit conversions shared by the comparison code.

Each method module keeps the constants printed in its own source (for example the
Self-Assessment Workbook converts Btu to kWh with 0.0002931). The standard conversion
factors below (1 hp = 745.699872 W; 1 Btu(IT) = 1055.05585 J; rounded) are used only when results from different
methods are put on a common kWh/yr basis. The circle area uses math.pi; Essentials v3
prints pi as 3.1416, which changes its flow by about -0.0002 %.
"""

import math

KW_PER_HP = 0.745699872          # mechanical horsepower (550 ft-lbf/s) in kW (rounded)
KWH_PER_MMBTU = 293.07107        # 1 MMBtu (IT Btu) in kWh (rounded)
HOURS_PER_YEAR = 8760
PSIA_STD_ATM = 14.7              # atmospheric pressure used by every source in this package


def hole_area_in2(diameter_in):
    """Area of a circular hole, in square inches."""
    if diameter_in <= 0:
        raise ValueError("diameter_in must be positive")
    return math.pi * diameter_in ** 2 / 4.0


def f_to_rankine(temp_f):
    """Degrees Fahrenheit to degrees Rankine, using +460 as the IAC sources do."""
    return temp_f + 460.0


def hp_to_kw(hp):
    return hp * KW_PER_HP


def mmbtu_to_kwh(mmbtu):
    return mmbtu * KWH_PER_MMBTU
