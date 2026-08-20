# -*- coding: utf-8 -*-
"""
Builds output/passport_filled.xlsx, output/passport.json and
output/building_meta.json from the transcribed BoQ data in data.py.

Run:  python src/build_passport.py
"""
import json
import os
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(__file__))
from data import RAW_ITEMS, BUILDING_META, subhead_for  # noqa: E402
from materials import factor_for, STANDARD_REFERENCE, MATERIAL_FACTORS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(ROOT, "AMP_Passport_Template.xlsx")
OUTPUT_DIR = os.path.join(ROOT, "output")
XLSX_OUT = os.path.join(OUTPUT_DIR, "passport_filled.xlsx")
JSON_OUT = os.path.join(OUTPUT_DIR, "passport.json")
META_OUT = os.path.join(OUTPUT_DIR, "building_meta.json")

UNIT_ALIASES = {
    "cu.m": "cum", "cum": "cum", "cu m": "cum",
    "sq.m": "sqm", "sqm": "sqm", "sq m": "sqm",
    "mtr.": "m", "mtr": "m", "m": "m",
    "kg.": "kg", "kg": "kg",
    "each": "nos", "no.": "nos", "nos": "nos",
}


def normalize_unit_qty(qty, unit):
    """Returns (norm_qty, norm_unit, derived_note or None)."""
    u = unit.strip()
    ul = u.lower()
    if ul == "100 sq.m":
        return qty * 100.0, "sqm", "unit conversion: quantity given as multiples of 100 Sq.m"
    if ul == "10 cubic decimetre":
        return qty * 0.01, "cum", "unit conversion: 10 Cubic decimetre = 0.01 cum (per template Instructions sheet)"
    norm = UNIT_ALIASES.get(ul)
    if norm:
        return qty, norm, None
    return qty, ul, None


def qty_columns(norm_qty, norm_unit):
    """Returns dict of P/Q/R/S/T column values."""
    cols = dict(volume=None, area=None, length=None, weight=None, count=None)
    if norm_unit == "cum":
        cols["volume"] = round(norm_qty, 4)
    elif norm_unit == "sqm":
        cols["area"] = round(norm_qty, 4)
    elif norm_unit == "m":
        cols["length"] = round(norm_qty, 4)
    elif norm_unit == "kg":
        cols["weight"] = round(norm_qty, 4)
    elif norm_unit == "nos":
        cols["count"] = norm_qty
    return cols


def thickness_m(dims):
    if not dims:
        return None
    for key in ("thickness_mm", "height_mm", "depth_mm"):
        if key in dims:
            return dims[key] / 1000.0
    return None


def carbon_bonus(category, mix, norm_unit, cols, dims, material_name):
    """Returns (density, embodied_carbon_kg, gwp_per_kg, source_note) or (None,None,None,None)."""
    factor = factor_for(category, mix)
    # per-item overrides not resolvable purely from category/mix:
    if factor is None:
        if category == "Roofing" and "clay" in material_name.lower():
            factor = MATERIAL_FACTORS["fired_clay_brick"]
        elif category == "Ironmongery" and "aluminium" in material_name.lower():
            factor = MATERIAL_FACTORS["aluminium_extrusion"]
        elif category == "Plumbing/Drainage" and ("cast iron" in material_name.lower() or material_name.lower().startswith("ci ")):
            factor = MATERIAL_FACTORS["cast_iron"]
    if factor is None:
        return None, None, None, None

    density = factor["density"]
    gwp = factor["gwp_per_kg"]
    weight_kg = None
    if norm_unit == "cum" and cols["volume"] is not None:
        weight_kg = cols["volume"] * density
    elif norm_unit == "sqm" and cols["area"] is not None:
        t = thickness_m(dims)
        if t:
            weight_kg = cols["area"] * t * density
    embodied = round(weight_kg * gwp, 2) if weight_kg is not None else None
    return density, embodied, gwp, factor["source"]


def build_rows():
    rows = []
    gmap_counter = 1
    for item in RAW_ITEMS:
        base = dict(item)
        sub_items = base.pop("sub_items", None)
        if sub_items:
            desc_common = base.get("desc_common", "")
            for sub in sub_items:
                merged = dict(base)
                merged.update(sub)
                merged["desc"] = (desc_common + " " + sub["desc"]).strip()
                merged["boq_no"] = f"{item['sl']}.{sub['letter']}"
                merged["dsr"] = sub.get("dsr", item.get("dsr", ""))
                if "material" not in merged or merged.get("material") == base.get("material"):
                    merged["material"] = sub.get("material", base.get("material"))
                rows.append(_finalize_row(gmap_counter, merged))
                gmap_counter += 1
        else:
            base["boq_no"] = item["sl"]
            rows.append(_finalize_row(gmap_counter, base))
            gmap_counter += 1
    return rows


def _finalize_row(gmap_counter, item):
    qty = item["qty"]
    unit = item["unit"]
    norm_qty, norm_unit, derived_note = normalize_unit_qty(qty, unit)
    cols = qty_columns(norm_qty, norm_unit)
    dims = item.get("dims", {})
    category = item.get("category", "")
    mix = item.get("mix")
    material_name = item.get("material", "")

    density, embodied, gwp, carbon_source = carbon_bonus(
        category, mix, norm_unit, cols, dims, material_name
    )

    comment_parts = []
    if item.get("excluded"):
        comment_parts.append(item.get("comment") or "[EXCLUDED]")
    elif item.get("comment"):
        comment_parts.append(item["comment"])
    if derived_note:
        comment_parts.append(derived_note)
    if carbon_source:
        comment_parts.append(f"[MASS&CARBON] {carbon_source}")
    comment = " | ".join(comment_parts) if comment_parts else None

    row = dict(
        gmap_id=f"GMAP-{gmap_counter:04d}",
        boq_item_no=item["boq_no"],
        article_number=None,
        external_db_id=None,
        description=item["desc"],
        floor_section=subhead_for(item.get("dsr", "")),
        discipline=item.get("discipline"),
        material_product=material_name,
        all_materials_detected=material_name,
        material_category=category,
        material_confidence="High" if not item.get("excluded") else "Medium",
        grade=None,
        mix_ratio=mix,
        original_quantity=qty,
        original_unit=unit,
        volume_m3=cols["volume"],
        area_m2=cols["area"],
        length_m=cols["length"],
        weight_kg=cols["weight"],
        count_nos=cols["count"],
        derived_quantity=round(norm_qty, 4) if derived_note else None,
        derived_quantity_unit=norm_unit if derived_note else None,
        derived_quantity_basis=derived_note,
        density_kg_m3=density,
        embodied_carbon_a1a3_kgco2e=embodied,
        gwp_per_kg_kgco2e=gwp,
        schedule="DSR 1989",
        schedule_item_code=item.get("dsr") or None,
        standard_code_reference=STANDARD_REFERENCE.get(category),
        classification_matched=item.get("classification"),
        pct_reused=None, pct_available_for_reuse=None, assumed_construction_waste=None,
        waste_codes=None, detach_connection=None, detach_connection_detail=None,
        detach_accessibility=None, detach_intersection=None, detach_product_edge=None,
        lifespan_years=None,
        length_mm=dims.get("length_mm"),
        width_mm=dims.get("width_mm"),
        height_mm=dims.get("height_mm"),
        thickness_mm=dims.get("thickness_mm"),
        depth_mm=dims.get("depth_mm"),
        diameter_mm=dims.get("diameter_mm"),
        unit_rate=None, total_cost=None, currency=None,
        comment=comment,
    )
    return row


COLUMN_ORDER = [
    "gmap_id", "boq_item_no", "article_number", "external_db_id", "description",
    "floor_section", "discipline", "material_product", "all_materials_detected",
    "material_category", "material_confidence", "grade", "mix_ratio",
    "original_quantity", "original_unit", "volume_m3", "area_m2", "length_m",
    "weight_kg", "count_nos", "derived_quantity", "derived_quantity_unit",
    "derived_quantity_basis", "density_kg_m3", "embodied_carbon_a1a3_kgco2e",
    "gwp_per_kg_kgco2e", "schedule", "schedule_item_code",
    "standard_code_reference", "classification_matched", "pct_reused",
    "pct_available_for_reuse", "assumed_construction_waste", "waste_codes",
    "detach_connection", "detach_connection_detail", "detach_accessibility",
    "detach_intersection", "detach_product_edge", "lifespan_years",
    "length_mm", "width_mm", "height_mm", "thickness_mm", "depth_mm",
    "diameter_mm", "unit_rate", "total_cost", "currency", "comment",
]

START_COL = "A"
LAST_COL = "AX"
START_ROW = 7  # rows 4-6 keep the template's own worked examples


def write_xlsx(rows):
    wb = openpyxl.load_workbook(TEMPLATE_PATH)
    ws = wb["Material Passport"]
    for i, row in enumerate(rows):
        r = START_ROW + i
        for col_idx, key in enumerate(COLUMN_ORDER, start=1):
            ws.cell(row=r, column=col_idx, value=row[key])
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wb.save(XLSX_OUT)
    print(f"Wrote {XLSX_OUT} ({len(rows)} data rows, starting at row {START_ROW})")


def write_json(rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Wrote {JSON_OUT} ({len(rows)} records)")


def write_meta():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(META_OUT, "w", encoding="utf-8") as f:
        json.dump(BUILDING_META, f, ensure_ascii=False, indent=2)
    print(f"Wrote {META_OUT}")


def main():
    rows = build_rows()
    n_boq_items = len(RAW_ITEMS)
    n_passport_rows = len(rows)
    print(f"Expanded {n_boq_items} BoQ Sl.No. items into {n_passport_rows} passport rows "
          f"({n_passport_rows - n_boq_items} extra rows from lettered sub-items).")
    write_xlsx(rows)
    write_json(rows)
    write_meta()


if __name__ == "__main__":
    main()
