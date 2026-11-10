"""Schmidt & Kissock: Moss equation and control-mode-corrected savings.

Sources
-------
[S2004] Schmidt, C., & Kissock, J. K. (2004). *Estimating Energy Savings in Compressed
        Air Systems*. University of Dayton, Mechanical and Aerospace Engineering
        Faculty Publications, Paper 145 (eCommons). The PDF has no printed page
        numbers; pages below are PDF pages (PDF p. 1 is the eCommons cover).
        * linear FP-FC model, Eq. (1)-(15): PDF pp. 3-5;
        * leak load from logged power: PDF pp. 7-8;
        * Moss equation, Eq. (16), 1/16-in example: PDF p. 8;
        * rule-of-thumb, modulation and load/unload leak examples: PDF pp. 8-9;
        * air-saver nozzle example (Moss with C = 0.9): PDF pp. 9-10.
[S2005] Schmidt, C., & Kissock, K. (2005). Modeling and Simulation of Air Compressor
        Energy Use. *ACEEE Summer Study on Energy Efficiency in Industry*, pp. 1-131 to
        1-142. Equation 1-4: p. 1-134; control-mode example: p. 1-135; demand-reduction
        example: p. 1-136; Figure 2 (FP vs FC by control type): p. 1-133.

Model
-----
    FP = FP0 + (1 - FP0) * FC          [S2005 Eq. 1; S2004 Eq. 1]
    FP = P / FLP,  FC = C / FLC,  FP0 = P0 / FLP     [S2005 Eq. 2-4]

Because the model is linear, cutting demand by dC lowers average power by
(1 - FP0) * FLP * dC / FLC, as long as FC stays within [0, 1].
"""

import math

from .units import hole_area_in2

# Moss equation constants [S2004 Eq. 16, PDF p. 8]
MOSS_CONSTANT = 0.5303             # lbm/s per (in2 * psia / R^0.5)
MOSS_TEMP_R = 530.0                # air temperature assumed by the equation, R
MOSS_DENSITY = 0.07494             # standard air density, lbm/ft3
C_ROUGH_LEAK = 0.61                # "a value for C of 0.61 is reasonable for leaks"
C_SMOOTH_TUBE = 0.9                # air-saver nozzle example, PDF p. 9

# Rule-of-thumb constants [S2004 PDF p. 8; S2005 p. 1-136]
CFM_PER_BHP = 4.2
KW_PER_HP_AS_PRINTED = 0.75
MOTOR_EFF = 0.90

# FP0 (fraction of full-load power at zero output) read off [S2005] Figure 2, p. 1-133.
# Read by eye from the plotted y-intercepts to the nearest 5 %; the paper gives no table, so
# these values can only be checked against the figure in the original PDF.
FP0_FIGURE2 = {
    "inlet_modulation": 0.70,
    "load_unload": 0.60,
    "variable_displacement": 0.25,
    "variable_speed": 0.10,
    "start_stop": 0.00,
}
# Ranges stated in the text
FP0_TEXT_RANGES = {
    "modulation": (0.60, 0.85),        # [S2004] PDF p. 5 ("between 60% and 85%")
    "load_unload": (0.20, 0.60),       # [S2004] PDF p. 5; [S2005] p. 1-132
    "inlet_modulation_2005": (0.65, 0.75),  # [S2005] p. 1-132
}


def moss_scfm(diameter_in, line_psia, c=C_ROUGH_LEAK):
    """Moss equation [S2004 Eq. 16], scfm:
        Q = 0.5303 * (pi/4) D^2 * C * P * 60 / (sqrt(530 R) * 0.07494 lb/ft3)
    The text layer of the PDF drops the square-root sign. The square root is required to
    reproduce the printed 3.96 scfm (SK04-1); the page image was checked by eye when this
    module was written but is not part of the package.
    """
    return MOSS_CONSTANT * hole_area_in2(diameter_in) * c * line_psia * 60.0 / (math.sqrt(MOSS_TEMP_R) * MOSS_DENSITY)


def fraction_power(fc, fp0):
    """FP = FP0 + (1 - FP0) * FC."""
    return fp0 + (1.0 - fp0) * fc


def fraction_capacity(fp, fp0):
    """Inverse of :func:`fraction_power`: FC = (FP - FP0) / (1 - FP0)."""
    return (fp - fp0) / (1.0 - fp0)


def demand_reduction_kw(flp_kw, flc_cfm, fp0, fc_before, delta_cfm):
    """Average-power reduction when demand falls by ``delta_cfm`` [S2004 PDF pp. 8-9; S2005 p. 1-136].

    Returns a dict with FC and power before and after. Raises if ``delta_cfm`` is negative or
    if FC before or after the change is outside [0, 1]."""
    if delta_cfm < 0:
        raise ValueError("delta_cfm must be a reduction (>= 0)")
    fc_after = fc_before - delta_cfm / flc_cfm
    if not (0.0 <= fc_after <= 1.0 and 0.0 <= fc_before <= 1.0):
        raise ValueError("FC outside [0, 1]: the single-compressor linear model does not apply")
    p_before = fraction_power(fc_before, fp0) * flp_kw
    p_after = fraction_power(fc_after, fp0) * flp_kw
    return {"fc_after": fc_after, "p_before_kw": p_before, "p_after_kw": p_after, "savings_kw": p_before - p_after}


def rule_of_thumb_kw(leak_cfm, cfm_per_bhp=CFM_PER_BHP, kw_per_hp=KW_PER_HP_AS_PRINTED, motor_eff=MOTOR_EFF):
    """"Rule-of-thumb" savings that ignore control mode [S2004 PDF p. 8; S2005 p. 1-136]:
        kW = (cfm / 4.2 cfm per bhp) * 0.75 kW/hp / 90 %
    The papers present this as the method that overestimates savings."""
    return leak_cfm / cfm_per_bhp * kw_per_hp / motor_eff


def control_corrected_kw(leak_cfm, fp0, cfm_per_bhp=CFM_PER_BHP, kw_per_hp=KW_PER_HP_AS_PRINTED, motor_eff=MOTOR_EFF):
    """Leak savings for a compressor described by FP0, sized by the same 4.2 cfm/bhp
    specific capacity: (1 - FP0) x rule-of-thumb kW. Equivalent to
    :func:`demand_reduction_kw` with FLP/FLC = kW per cfm at full load."""
    return (1.0 - fp0) * rule_of_thumb_kw(leak_cfm, cfm_per_bhp, kw_per_hp, motor_eff)
