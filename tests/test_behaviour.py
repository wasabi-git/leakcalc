"""Behaviour that the sources imply but do not illustrate with a printed example."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from leakcalc import compare, essentials, schmidt, tipsheet, ump, workbook  # noqa: E402


class Guards(unittest.TestCase):
    def test_essentials_requires_choked_flow(self):
        # 10 psig: 14.7 / 24.7 = 0.595 > 0.5283, not choked
        with self.assertRaises(ValueError):
            essentials.free_air_flow_cfm(1 / 8, 10, 70, 70)

    def test_tipsheet_no_interpolation(self):
        with self.assertRaises(KeyError):
            tipsheet.leakage_cfm(1 / 8, 110)
        with self.assertRaises(KeyError):
            tipsheet.leakage_cfm(3 / 16, 100)

    def test_ump_requires_orifice_factor(self):
        with self.assertRaises(ValueError):
            ump.table6_cfm(1 / 8, 100, "table")

    def test_schmidt_fc_out_of_range(self):
        with self.assertRaises(ValueError):
            schmidt.demand_reduction_kw(52, 265, 0.55, 0.2, 70)      # FC after < 0
        with self.assertRaises(ValueError):
            schmidt.demand_reduction_kw(52, 265, 0.55, 0.5, -265)    # negative reduction, FC after 1.5
        with self.assertRaises(ValueError):
            schmidt.demand_reduction_kw(52, 265, 0.55, 1.2, 10)      # FC before > 1
        with self.assertRaises(ValueError):
            schmidt.demand_reduction_kw(52, 265, 0.55, -0.1, 0)      # FC before < 0

    def test_tipsheet_rejects_unlisted_diameters(self):
        # 0.124 in must not be silently rounded to the 1/8-in column (Codex review 2026-11-10)
        for d in (0.124, 0.126, 0.13, 0.3):
            with self.assertRaises(KeyError):
                tipsheet.leakage_cfm(d, 100)
        self.assertEqual(tipsheet.leakage_cfm(0.125, 100, "table"), 25.22)
        self.assertFalse(tipsheet.has_cell(0.124, 100))
        self.assertTrue(tipsheet.has_cell(1 / 8, 100))


class IndependentValues(unittest.TestCase):
    """Values written out by hand from the source, not taken from the package's own tables."""

    def test_ump_leakdown_equation_11(self):
        # V = 100 ft3, dP = 50 psi, 2 min, Palt 14.7 psia: (100 x 50) / (2 x 14.7) x 1.25 = 212.585034...
        self.assertTrue(math.isclose(ump.leakdown_scfm(100, 50, 2), 6250 / 29.4, rel_tol=1e-12))
        # altitude: Palt 12.2 psia
        self.assertTrue(math.isclose(ump.leakdown_scfm(40, 30, 3, p_alt_psia=12.2), 1500 / 36.6, rel_tol=1e-12))

    def test_essentials_table_6_3_as_printed(self):
        # Essentials v3 Table 6.3, printed p. 189 (PDF p. 200)
        printed = {3 / 8: (90_400_000, 29.9), 1 / 4: (40_300_000, 14.2), 1 / 8: (10_020_000, 3.4),
                   1 / 16: (2_580_000, 0.9), 1 / 32: (625_000, 0.2)}
        self.assertEqual(essentials.NBS_TABLE_100PSI, printed)
        for d, (_, kwh_h) in printed.items():
            self.assertEqual(essentials.nbs_table_kwh(d, 1000), kwh_h * 1000)

    def test_tipsheet_cells_spot_check(self):
        # DOE Tip Sheet #3 table, p. 1: one cell per row and both orifice factors, typed from the source
        for p, d, v in ((70, 1 / 64, 0.29), (80, 1 / 16, 5.24), (90, 1 / 8, 23.10), (100, 1 / 4, 100.9), (125, 3 / 8, 275.5)):
            self.assertEqual(tipsheet.leakage_cfm(d, p, "table"), v)
        self.assertEqual(tipsheet.ORIFICE_FACTOR["rounded"], 0.97)
        self.assertEqual(tipsheet.ORIFICE_FACTOR["sharp"], 0.61)


class Physics(unittest.TestCase):
    def test_flow_scales_with_diameter_squared(self):
        for f in (lambda d: essentials.free_air_flow_cfm(d, 100, 70, 70),
                  lambda d: workbook.mass_flow_lbm_hr(d, 114.7, 70),
                  lambda d: schmidt.moss_scfm(d, 114.7)):
            self.assertTrue(math.isclose(f(1 / 4) / f(1 / 8), 4.0, rel_tol=1e-12))

    def test_essentials_equals_moss_family_at_same_temperature(self):
        # With Ti = Tl the Essentials equation is the textbook sonic-orifice flow; the Moss
        # equation is the same physics with C and 530 R. Ratio should be Cd/C x small constant diff.
        es = essentials.free_air_flow_cfm(1 / 8, 100, 70, 70, cd=0.61)
        mo = schmidt.moss_scfm(1 / 8, 114.7, c=0.61)
        self.assertTrue(math.isclose(es, mo, rel_tol=0.01), (es, mo))

    def test_essentials_flow_matches_first_principles(self):
        # The Essentials worked example cannot check the flow equation (ESS-1 is a documented
        # mismatch), so check it against choked-flow gas dynamics instead:
        #   C4 = sqrt(k R gc) * (2/(k+1))^((k+1)/(2(k-1))),  R = 53.35 ft-lbf/(lbm R), gc = 32.174
        k, r, gc = 1.4, 53.35, 32.174
        c4 = math.sqrt(k * r * gc) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))
        self.assertTrue(math.isclose(c4, essentials.C4_SONIC, rel_tol=5e-4), c4)
        # Free-air flow = Cd * A * (Pl/Pi) * Ti / sqrt(Tl) * C4 * 60, A in ft2
        for d, psig, ti, tl in ((1 / 8, 100, 70, 70), (1 / 4, 115, 92, 72), (1 / 32, 90, 60, 100)):
            area_ft2 = math.pi * d ** 2 / 4 / 144
            q = 0.8 * area_ft2 * (psig + 14.7) / 14.7 * (ti + 460) / math.sqrt(tl + 460) * c4 * 60
            self.assertTrue(math.isclose(essentials.free_air_flow_cfm(d, psig, ti, tl), q, rel_tol=5e-4))

    def test_linear_model_saving_independent_of_baseline(self):
        a = schmidt.demand_reduction_kw(52, 265, 0.55, 0.9, 70)["savings_kw"]
        b = schmidt.demand_reduction_kw(52, 265, 0.55, 0.5, 70)["savings_kw"]
        self.assertTrue(math.isclose(a, b, rel_tol=1e-12))
        self.assertTrue(math.isclose(a, 0.45 * 52 * 70 / 265, rel_tol=1e-12))

    def test_ump_table6_equals_tipsheet(self):
        for p in tipsheet.LEAKAGE_CFM:
            for d in tipsheet.DIAMETERS:
                self.assertEqual(ump.table6_cfm(d, p, "sharp"), tipsheet.leakage_cfm(d, p, "sharp"))


class ReferenceComparison(unittest.TestCase):
    """Pins the numbers reported in docs/algorithm_comparison.md."""

    def test_core_spread(self):
        rows = compare.run()
        ratio, lo, hi = compare.spread(rows, "core")
        self.assertTrue(math.isclose(lo, 13494.4, rel_tol=1e-4), lo)
        self.assertTrue(math.isclose(hi, 38573.6, rel_tol=1e-4), hi)
        self.assertTrue(math.isclose(ratio, hi / lo))


if __name__ == "__main__":
    unittest.main()
