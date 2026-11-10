"""leakcalc: reference implementations of published methods for estimating the
energy savings from repairing compressed-air leaks.

Every function implements one equation or table from one published source, keeps
that source's own constants as defaults, and cites the source and page in its
docstring. The package does not choose a "best" method; it makes the published
methods easy to compare on identical inputs.

Modules
-------
essentials  IAC training manual "Essentials of Industrial Assessments" v3.0 (2015):
            choked (sonic) orifice flow + adiabatic compression power.
workbook    "Self-Assessment Workbook for Small Manufacturers" v2.0 (2003):
            Fliegner's formula + isothermal compression energy.
tipsheet    DOE Compressed Air Tip Sheet #3 (2004): leakage-rate table x kW/cfm.
ump         Uniform Methods Project Chapter 22 (NREL/SR-7A40-77820, 2021):
            leak-down test, simplified savings with control adjustment factor (CCAF).
schmidt     Schmidt & Kissock (2004, 2005): Moss equation and the linear
            part-load (FP-FC) compressor model that corrects savings for control type.
compare     The same leak evaluated by every method (used for docs/algorithm_comparison.md).
"""

__version__ = "0.1.0"

from . import compare, essentials, schmidt, tipsheet, ump, units, workbook  # noqa: F401
