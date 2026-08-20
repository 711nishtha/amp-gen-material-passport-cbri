# -*- coding: utf-8 -*-
"""
Bonus B2 - Mass & Carbon reference data for the AMBER (bonus) columns.

Each entry gives a cradle-to-gate (A1-A3) embodied-carbon factor (GWP per kg)
and a typical bulk density, with a citable source. These are published,
commonly-cited generic factors (NOT product-specific EPDs, which do not
exist for a 1989-era Roorkee residence) - this is disclosed in APPROACH.md.

Sources:
  ICE  = Inventory of Carbon and Energy, Database V3.0, Circular Ecology /
         University of Bath (Jones & Hammond, 2019).
  IS   = relevant Indian Standard, cited only for the density/classification,
         not the carbon figure.
"""

MATERIAL_FACTORS = {
    "steel_rebar": dict(
        density=7850, gwp_per_kg=2.363,
        source="ICE Database V3.0 - Reinforcing steel (rebar, virgin), "
               "same factor as used in the template's own worked example (row 6).",
    ),
    "fired_clay_brick": dict(
        density=1750, gwp_per_kg=0.24,
        source="ICE Database V3.0 - Brick (common, fired clay), 0.24 kgCO2e/kg.",
    ),
    "aluminium_extrusion": dict(
        density=2700, gwp_per_kg=8.24,
        source="ICE Database V3.0 - Aluminium (general, incl. typical recycled content), 8.24 kgCO2e/kg.",
    ),
    "cast_iron": dict(
        density=7150, gwp_per_kg=1.91,
        source="ICE Database V3.0 - Cast iron, 1.91 kgCO2e/kg.",
    ),
    "hardwood_timber": dict(
        density=650, gwp_per_kg=0.45,
        source="ICE Database V3.0 - Hardwood (general, sawn), 0.45 kgCO2e/kg.",
    ),
    # Nominal-mix cement concrete, keyed by mix ratio; grade-equivalence per
    # IS 456:2000 Table 9, GWP mapped from ICE V3 concrete-by-strength series.
    "concrete_1:5:10": dict(density=2400, gwp_per_kg=0.070,
        source="ICE Database V3.0 concrete series, ~M5-equivalent nominal mix (IS 456 Table 9), 0.070 kgCO2e/kg."),
    "concrete_1:4:8": dict(density=2400, gwp_per_kg=0.083,
        source="ICE Database V3.0 concrete series, ~M7.5-equivalent nominal mix (IS 456 Table 9), 0.083 kgCO2e/kg."),
    "concrete_1:3:6": dict(density=2400, gwp_per_kg=0.095,
        source="ICE Database V3.0 concrete series, ~M10-equivalent nominal mix (IS 456 Table 9), 0.095 kgCO2e/kg."),
    "concrete_1:2:4": dict(density=2400, gwp_per_kg=0.107,
        source="ICE Database V3.0 concrete series, ~M15-equivalent nominal mix (IS 456 Table 9), 0.107 kgCO2e/kg."),
}

# Map material category / mix -> factor key, applied in build_passport.py
def factor_for(category: str, mix: str = None):
    if category == "Reinf":
        return MATERIAL_FACTORS["steel_rebar"]
    if category == "Masonry":
        return MATERIAL_FACTORS["fired_clay_brick"]
    if category == "Roofing" and mix is None:
        return None  # handled per-item (clay tile uses same factor as brick)
    if category in ("Timber/Joinery",):
        return MATERIAL_FACTORS["hardwood_timber"]
    if category == "Ironmongery":
        return None  # mixed materials (MS/aluminium), handled per item below
    if category == "Plumbing/Drainage":
        return None  # handled per item (cast iron vs MS)
    if mix and f"concrete_{mix}" in MATERIAL_FACTORS:
        return MATERIAL_FACTORS[f"concrete_{mix}"]
    return None


STANDARD_REFERENCE = {
    "Earthwork": None,
    "Earthwork Fill": "IS 1498",
    "Chemical Treatment": "IS 6313 (Part 2)",
    "Concrete": "IS 456:2000",
    "Reinf": "IS 1786 (TMT/CTD bars)",
    "Formwork": None,
    "Masonry": "IS 1077 / IS 2212",
    "Timber/Joinery": "IS 883",
    "Ironmongery": "IS 205 / IS 281 / IS 1868 (aluminium anodising)",
    "Metal Windows/Glazing": "IS 1038",
    "Metalwork": "IS 226 (structural steel)",
    "Flooring/Concrete": "IS 456:2000",
    "Plaster": "IS 1661",
    "Flooring/Stone": "IS 1237 (terrazzo tiles/in-situ)",
    "Flooring Accessory": None,
    "Waterproofing": "IS 73 (bitumen)",
    "Roofing": "IS 1478 (clay roofing tiles)",
    "Roof Drainage": "IS 15834",
    "Plumbing/Drainage": "IS 1729 (CI pipes/fittings)",
    "Paint/Finish": "IS 428 / IS 2338",
}
