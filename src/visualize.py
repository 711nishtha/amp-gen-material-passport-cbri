# -*- coding: utf-8 -*-
"""
Builds output/visualization.png - material distribution across the building
by Discipline, broken down by Material Category (stacked bar, item count).

Run:  python src/visualize.py
"""
import json
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_IN = os.path.join(ROOT, "output", "passport.json")
PNG_OUT = os.path.join(ROOT, "output", "visualization.png")

CATEGORY_COLORS = {
    "Earthwork": "#8d6e63",
    "Earthwork Fill": "#bcaaa4",
    "Chemical Treatment": "#a1887f",
    "Concrete": "#78909c",
    "Reinf": "#455a64",
    "Formwork": "#cfd8dc",
    "Masonry": "#c0704d",
    "Timber/Joinery": "#c9a227",
    "Ironmongery": "#7e8ca3",
    "Metal Windows/Glazing": "#4f6d8f",
    "Metalwork": "#37474f",
    "Flooring/Concrete": "#607d8b",
    "Plaster": "#b0bec5",
    "Flooring/Stone": "#8e7cc3",
    "Flooring Accessory": "#b39ddb",
    "Waterproofing": "#2f3e46",
    "Roofing": "#a35d3b",
    "Roof Drainage": "#546e7a",
    "Plumbing/Drainage": "#3f6b8c",
    "Paint/Finish": "#e0a458",
}


def main():
    rows = json.load(open(JSON_IN, encoding="utf-8"))

    counts = defaultdict(lambda: defaultdict(int))
    categories_seen = []
    for r in rows:
        disc = r["discipline"] or "Unclassified"
        cat = r["material_category"] or "Unclassified"
        counts[disc][cat] += 1
        if cat not in categories_seen:
            categories_seen.append(cat)

    disciplines = sorted(counts.keys(), key=lambda d: -sum(counts[d].values()))
    categories_seen.sort()

    fig, ax = plt.subplots(figsize=(11, 6.5))
    left = [0] * len(disciplines)
    for cat in categories_seen:
        vals = [counts[d].get(cat, 0) for d in disciplines]
        if sum(vals) == 0:
            continue
        color = CATEGORY_COLORS.get(cat, "#999999")
        ax.barh(disciplines, vals, left=left, label=cat, color=color, edgecolor="white", height=0.62)
        left = [l + v for l, v in zip(left, vals)]

    ax.set_xlabel("Number of Material Passport rows (BoQ line items, sub-items expanded)")
    ax.set_title(
        "AMP-GEN Material Passport — Principal's Residence, CBRI Roorkee\n"
        "Material distribution by Discipline and Material Category (n=74 rows from 64 BoQ items)",
        fontsize=12, fontweight="bold", loc="left"
    )
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8, title="Material Category", frameon=False)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for i, d in enumerate(disciplines):
        total = sum(counts[d].values())
        ax.text(total + 0.4, i, str(total), va="center", fontsize=9, color="#333")

    fig.text(0.01, 0.01,
              "Source: BoQ_CBRI_Principals_Residence.pdf (DSR 1989) — hand-transcribed extraction. "
              "[EXCLUDED] earthwork/labour-only items retained in count but carry no material mass.",
              fontsize=7, color="#666")

    plt.tight_layout(rect=[0, 0.03, 1, 1])
    os.makedirs(os.path.dirname(PNG_OUT), exist_ok=True)
    plt.savefig(PNG_OUT, dpi=180, bbox_inches="tight")
    print(f"Wrote {PNG_OUT}")


if __name__ == "__main__":
    main()
