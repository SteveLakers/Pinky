#!/usr/bin/env python3
"""
Fill the product page (product/index.html) with numbers from artifacts/product_numbers.json.

Two jobs, so nothing on the page is typed by hand:
  1. Rewrites the `const DATA = …` block between `// DATA:BEGIN` and `// DATA:END` (chart data).
  2. Rewrites the text of every element tagged `data-v="path|format"`, e.g.
     <b data-v="cagr.current.all|pct1s">+7.2%</b>  ->  formatted value of DATA.cagr.current.all.

Prints every text that changed. Run scripts/product_numbers.py first if the runs changed.

Usage: python scripts/product_page_data.py [--check]   (--check: report only, don't write)
"""

from __future__ import annotations

import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMBERS = ROOT / "artifacts" / "product_numbers.json"
PAGE = ROOT / "product" / "index.html"
MINUS = "−"
SECTOR_NAMES = {
    "Technology": "Tech", "Healthcare": "Healthcare", "Financial Services": "Banks & finance",
    "Industrials": "Industrials", "Consumer Cyclical": "Consumer cyclical", "Energy": "Energy",
    "Basic Materials": "Materials", "Real Estate": "Real estate", "Communication Services": "Communication",
    "Consumer Defensive": "Consumer staples", "Utilities": "Utilities",
}


def build(n: dict) -> dict:
    halves = lambda s, k="cagr_net": {"all": s["all"][k], "a": s["2001–2008"][k], "b": s["2009–2020"][k]}
    calm = n["calm_current"]
    d: dict = {
        "growth": {k: [round(v) for v in n["growth_10k"][src]] for k, src in
                   (("best", "best"), ("current", "current"), ("hunter", "hunter"), ("spy", "spy"), ("every", "every_stock"))},
        "cagr": {"best": halves(n["best_v6_ridge"]), "current": halves(calm), "hunter": halves(n["hunter"]),
                 "spy": halves(calm, "cagr_spy"), "every": halves(calm, "cagr_universe_ew")},
        "fancyFair": n["fancy_v6_lgbm_top10_buffer"]["all"]["cagr_net"],
        "universe": {int(y): v for y, v in n["universe_by_year"].items()},
        "ic": [n["ic_by_year_calm"][str(y)] for y in range(2001, 2021)],
        "groups": [g["beat_spy"] for g in n["score_groups_calm"][:10]],
        "groupsAll": next(g["beat_spy"] for g in n["score_groups_calm"] if g["group"] == "All stocks"),
        "fates": n["fates_test"],
        "rates": {k: n[src] for k, src in (("random", "random_big_crash"), ("fancy", "fancy_v6_big_crash"),
                                           ("calm", "calm_big_crash"), ("hunter", "hunter_big_crash"))},
        "takeover": {"simple": n["simple_v6_acquired_top10"], "base": n["acquired_base_rate"]},
        "gt": {name: {kind: {"all": n[f"growth_{name}_{kind}"]["all"], "a": n[f"growth_{name}_{kind}"]["2001–2008"],
                             "b": n[f"growth_{name}_{kind}"]["2009–2020"]} for kind in ("real", "placebo")}
               for name in ("calm", "hunter")},
        "counts": {"snapshots": n["snapshots_last_fold"], "scored": n["snapshots_scored"],
                   "perDate": n["stocks_per_date"], "distinct": n["universe_distinct"], "picks": n["avg_picks_current"]},
    }
    sec = n["sectors"]
    d["sectors"] = [[SECTOR_NAMES[k], round(100 * v, 1), round(100 * sec["calm"][k], 1), round(100 * sec["hunter"][k], 1)]
                    for k, v in sec["market"].items() if k in SECTOR_NAMES]
    g, f, ic = d["growth"], d["fates"], d["ic"]
    by = {s[0]: s for s in d["sectors"]}
    d["x"] = {  # derived numbers the page text uses
        "lead2009": g["best"][96] / g["spy"][96] - 1,
        "leadEnd": g["best"][-1] / g["spy"][-1] - 1,
        "gone": f["total"] - f["still_trade"],
        "goneShare": (f["total"] - f["still_trade"]) / f["total"],
        "icMean": sum(ic) / len(ic),
        "icPos": sum(v > 0 for v in ic),
        "ic2020": ic[-1],
        "groupLow": d["groups"][0] - d["groupsAll"],
        "groupHigh": d["groups"][9] - d["groupsAll"],
        "gapCalm": d["gt"]["calm"]["real"]["all"] - d["gt"]["calm"]["placebo"]["all"],
        "gapHunter": d["gt"]["hunter"]["real"]["all"] - d["gt"]["hunter"]["placebo"]["all"],
        "calmCost": d["cagr"]["current"]["all"] - d["gt"]["calm"]["real"]["all"],
        "utilX": by["Utilities"][2] / by["Utilities"][1],
        "reX": by["Real estate"][2] / by["Real estate"][1],
        "techX": by["Tech"][2] / by["Tech"][1],
    }
    return d


def q(v: float, places: int) -> Decimal:
    return Decimal(repr(v)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def signed(v: Decimal) -> str:
    return ("+" if v > 0 else MINUS if v < 0 else "") + str(abs(v))


FORMATS = {
    "pct0s": lambda v: signed(q(v * 100, 0)) + "%",
    "pct1s": lambda v: signed(q(v * 100, 1)) + "%",
    "pct2s": lambda v: signed(q(v * 100, 2)) + "%",
    "pct0": lambda v: str(q(v * 100, 0)) + "%",
    "pct1": lambda v: str(q(v * 100, 1)) + "%",
    "pct2": lambda v: str(q(v * 100, 2)) + "%",
    "num1": lambda v: str(q(v * 100, 1)),       # a rate as a bare number: 0.0723 -> 7.2
    "pp1s": lambda v: signed(q(v * 100, 1)),    # a rate difference in points: -0.0524 -> −5.2
    "per100": lambda v: str(q(v * 100, 0)),     # a rate as "out of 100": 0.1854 -> 19
    "int": lambda v: f"{int(q(v, 0)):,}",
    "money": lambda v: f"${int(q(v, 0)):,}",
    "x1": lambda v: str(q(v, 1)) + "×",
    "ic2s": lambda v: signed(q(v, 2)),
}


def lookup(d: dict, path: str):
    v = d
    for part in path.split("."):
        v = v[int(part)] if isinstance(v, list) else v[part]
    return v


def main() -> None:
    check = "--check" in sys.argv
    d = build(json.loads(NUMBERS.read_text()))
    html = PAGE.read_text()

    block = "// DATA:BEGIN (scripts/product_page_data.py; don't edit by hand)\nconst DATA = " + \
        json.dumps(d, separators=(",", ":"), ensure_ascii=False) + ";\n// DATA:END"
    html, k = re.subn(r"// DATA:BEGIN.*?// DATA:END", lambda _: block, html, flags=re.S)
    if k != 1:
        sys.exit(f"expected one DATA block, found {k}")

    changed = []

    def fill(m: re.Match) -> str:
        path, fmt = m.group(3), m.group(4)
        new = FORMATS[fmt](lookup(d, path)).replace("&", "&amp;")
        if new != m.group(5):
            changed.append(f"{path}|{fmt}: {m.group(5)!r} -> {new!r}")
        return m.group(1) + new + m.group(6)

    pattern = r'(<(\w+)\b[^>]*?\bdata-v="([^"|]+)\|(\w+)"[^>]*>)([^<]*)(</\2>)'
    html, bound = re.subn(pattern, fill, html)
    print(f"{bound} bound numbers, {len(changed)} changed")
    for c in changed:
        print("  " + c)
    if not check:
        PAGE.write_text(html)
        print(f"Wrote {PAGE}")


if __name__ == "__main__":
    main()
