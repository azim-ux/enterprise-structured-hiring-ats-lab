import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ("index.html", "dashboard.html")


def responsive_overflow_contract(source):
    chart_match = re.search(r"\.chart-card\s*\{([^}]*)\}", source)
    drawer_match = re.search(r"\.drawer-layer\s*\{([^}]*)\}", source)
    pager_match = re.search(r"\.pager button\s*\{([^}]*)\}", source)
    if not chart_match or not drawer_match or not pager_match:
        return False

    chart_declarations = chart_match.group(1).replace(" ", "")
    drawer_declarations = drawer_match.group(1).replace(" ", "")
    pager_declarations = pager_match.group(1).replace(" ", "")
    return (
        "min-width:0" in chart_declarations
        and "overflow:hidden" in drawer_declarations
        and "min-width:44px" in pager_declarations
    )


class DashboardResponsiveTests(unittest.TestCase):
    def test_dashboard_routes_enforce_narrow_resize_overflow_contract(self):
        for route in ROUTES:
            with self.subTest(route=route):
                source = (ROOT / route).read_text(encoding="utf-8")
                self.assertTrue(responsive_overflow_contract(source))

    def test_contract_rejects_missing_grid_shrink_or_drawer_containment(self):
        valid = (
            ".chart-card{min-height:370px;padding:22px;min-width:0}"
            ".drawer-layer{position:fixed;overflow:hidden}"
            ".pager button{min-width:44px;height:34px}"
        )
        self.assertTrue(responsive_overflow_contract(valid))
        self.assertFalse(
            responsive_overflow_contract(valid.replace("min-width:0", ""))
        )
        self.assertFalse(
            responsive_overflow_contract(valid.replace("overflow:hidden", ""))
        )
        self.assertFalse(
            responsive_overflow_contract(valid.replace("min-width:44px", "min-width:36px"))
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
