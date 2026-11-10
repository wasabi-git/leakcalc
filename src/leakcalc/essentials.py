"""IAC training manual method: choked orifice flow and adiabatic compression power.

Source
------
Muller, M. R., Simek, M., Mak, J., & Mitrovic, B. (2015). *Essentials of Industrial
Assessments: A Training Manual*, Version 3.0. Center for Advanced Energy Systems,
Rutgers University (running title "Modern Industrial Assessments").
Section "Elimination of Air Leaks", printed pp. 188-198 (PDF pp. 199-209):

* case-study inputs and results table: printed pp. 192-194 (PDF pp. 203-205);
* flow equation: printed p. 195 (PDF p. 206);
* power equation and compressor efficiencies: printed pp. 196-197 (PDF pp. 207-208);
* annual energy: printed p. 198 (PDF p. 209).

Notes on transcription
----------------------
* The flow equation divides by "C6"; the symbol list on p. 196 calls the same
  constant "Cb = 144 in2/ft2". Both are the in2-to-ft2 conversion; this module calls
  it ``IN2_PER_FT2``. The power equation also uses C6 = 144 (psi to lbf/ft2).
* Temperatures are converted with +460, as printed.
"""

import math

from .units import PSIA_STD_ATM, f_to_rankine, hole_area_in2

C4_SONIC = 28.37          # isentropic sonic volumetric flow constant, ft/(s*R^0.5), p. 196
C5_S_PER_MIN = 60.0       # p. 196
IN2_PER_FT2 = 144.0       # "C6" / "Cb", p. 195-196
C7_HP_MIN_PER_FT_LBF = 3.03e-5   # p. 196
C8_MMBTU_PER_HP_H = 0.002545     # p. 198
CD_SQUARE_EDGED = 0.8     # coefficient of discharge, square-edged orifice, p. 196
K_AIR = 1.4               # specific heat ratio, p. 196
CHOKED_PRESSURE_RATIO = 0.5283   # p. 195

# Adiabatic (isentropic) efficiencies, p. 196-197
ADIABATIC_EFFICIENCY = {
    "reciprocating_single_stage": 0.88,
    "reciprocating_multi_stage": 0.75,
    "rotary_screw": 0.82,
    "sliding_vane": 0.72,
    "centrifugal_single_stage": 0.80,
    "centrifugal_multi_stage": 0.70,
    "turbo_blower": 0.70,
    "roots_blower": 0.62,
}


def is_choked(line_psia, atm_psia=PSIA_STD_ATM):
    """Flow is choked when atmospheric / line pressure < 0.5283 (p. 195)."""
    return atm_psia / line_psia < CHOKED_PRESSURE_RATIO


def free_air_flow_cfm(diameter_in, line_psig, inlet_temp_f, line_temp_f, n_leaks=1,
                      atm_psia=PSIA_STD_ATM, cd=CD_SQUARE_EDGED):
    """Volumetric flow of free air through a leak under choked flow, cfm (p. 195).

        Vf = NL * (Ti + 460) * (Pl / Pi) * C4 * C5 * Cd * (pi D^2 / 4) / (C6 * sqrt(Tl + 460))

    Raises ValueError if the flow is not choked; the manual gives no equation for
    unchoked flow.
    """
    line_psia = line_psig + atm_psia
    if not is_choked(line_psia, atm_psia):
        raise ValueError("flow is not choked (Pi/Pl >= 0.5283); the manual's equation does not apply")
    return (n_leaks * f_to_rankine(inlet_temp_f) * (line_psia / atm_psia) * C4_SONIC * C5_S_PER_MIN * cd
            * hole_area_in2(diameter_in) / (IN2_PER_FT2 * math.sqrt(f_to_rankine(line_temp_f))))


def power_loss_hp(free_air_cfm, discharge_psig, adiabatic_eff, motor_eff, stages=1,
                  atm_psia=PSIA_STD_ATM, k=K_AIR):
    """Electrical power needed to compress the leaked air, hp (p. 196).

        L = Pi*C6*Vf * k/(k-1) * N * C7 * [ (Po/Pi)^((k-1)/(k*N)) - 1 ] / (Ea * Em)
    """
    po_psia = discharge_psig + atm_psia
    work = (atm_psia * IN2_PER_FT2 * free_air_cfm * k / (k - 1) * stages * C7_HP_MIN_PER_FT_LBF
            * ((po_psia / atm_psia) ** ((k - 1) / (k * stages)) - 1.0))
    return work / (adiabatic_eff * motor_eff)


def annual_energy_mmbtu(power_hp, hours):
    """ES = L * H * C8, MMBtu/yr (p. 198)."""
    return power_hp * hours * C8_MMBTU_PER_HP_H


def annual_energy_kwh(power_hp, hours):
    """Same as :func:`annual_energy_mmbtu` but reported in kWh/yr (hp * h * 0.7457 kW/hp).

    The manual reports MMBtu with C8 = 0.002545 MMBtu/hp-h, which equals
    0.7459 kWh/hp-h; this function uses the standard 0.745700 so that results are
    comparable with the other methods. The difference is about 0.02 %.
    """
    from .units import KW_PER_HP
    return power_hp * hours * KW_PER_HP


def leak_savings(diameter_in, line_psig, hours, inlet_temp_f, line_temp_f, adiabatic_eff, motor_eff,
                 discharge_psig=None, stages=1, n_leaks=1, atm_psia=PSIA_STD_ATM, cd=CD_SQUARE_EDGED):
    """Convenience wrapper: flow (cfm), power (hp), energy (MMBtu/yr and kWh/yr).

    ``discharge_psig`` defaults to the line pressure (the case study sets both to 115 psig).
    """
    if discharge_psig is None:
        discharge_psig = line_psig
    vf = free_air_flow_cfm(diameter_in, line_psig, inlet_temp_f, line_temp_f, n_leaks, atm_psia, cd)
    hp = power_loss_hp(vf, discharge_psig, adiabatic_eff, motor_eff, stages, atm_psia)
    return {"flow_cfm": vf, "power_hp": hp, "energy_mmbtu": annual_energy_mmbtu(hp, hours),
            "energy_kwh": annual_energy_kwh(hp, hours)}


# Table 6.3, printed p. 189 (PDF p. 200), "Source: National Bureau of Standards", 100 psi.
# diameter (in) -> (free air wasted ft3/yr, energy wasted kWh per hour per leak)
NBS_TABLE_100PSI = {
    3 / 8: (90_400_000, 29.9),
    1 / 4: (40_300_000, 14.2),
    1 / 8: (10_020_000, 3.4),
    1 / 16: (2_580_000, 0.9),
    1 / 32: (625_000, 0.2),
}


def nbs_table_kwh(diameter_in, hours):
    """Annual energy from Table 6.3 (100 psi only): kWh/h per leak x hours."""
    if diameter_in not in NBS_TABLE_100PSI:
        raise KeyError(f"Table 6.3 has no row for {diameter_in} in; rows: {sorted(NBS_TABLE_100PSI)}")
    return NBS_TABLE_100PSI[diameter_in][1] * hours
