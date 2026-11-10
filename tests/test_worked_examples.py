"""Unit tests: every worked example printed in the official sources (see examples.py).

For ``match=True`` the recomputed value must equal the printed value within the
stated rounding tolerance. For ``match=False`` the test asserts that the documented
mismatch is real, so a later change cannot silently "fix" an equation to agree with
a printed number, and that the recomputed value equals the one stated in the
documentation (``computed``).

Run:  python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from examples import EXAMPLES, within  # noqa: E402


class WorkedExamples(unittest.TestCase):
    def test_ids_unique(self):
        ids = [e["id"] for e in EXAMPLES]
        self.assertEqual(len(ids), len(set(ids)))


def _make(ex):
    def test(self):
        v = ex["value"]()
        if ex["match"]:
            self.assertTrue(within(v, ex["printed"], ex["rtol"]),
                            f"{ex['id']}: computed {v!r}, printed {ex['printed']!r}, rtol {ex['rtol']}")
        else:
            self.assertFalse(within(v, ex["printed"], ex["rtol"]),
                             f"{ex['id']}: documented as a mismatch but now agrees ({v!r} vs {ex['printed']!r})")
            # also pin the value the documentation reports, so a broken formula cannot pass by
            # merely disagreeing with the printed number
            self.assertTrue(within(v, ex["computed"], 5e-4),
                            f"{ex['id']}: computed {v!r}, documented {ex['computed']!r}")
    test.__doc__ = f"{ex['id']} {ex['what']}"
    return test


for _ex in EXAMPLES:
    setattr(WorkedExamples, "test_" + _ex["id"].replace("-", "_"), _make(_ex))


if __name__ == "__main__":
    unittest.main()
