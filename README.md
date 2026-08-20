# AMP-GEN Material Passport — Principal's Residence, CBRI Roorkee

Extracts all 64 line items from the scanned 1989 Bill of Quantities (`BoQ_CBRI_Principals_Residence.pdf`)
into the `AMP_Passport_Template.xlsx` Material Passport schema, exports the same data as JSON, and
produces a material-distribution chart.

**Live demo (Bonus B1):** _<paste your Hugging Face Space URL here>_

## Run it (< 5 minutes)

```bash
pip install -r requirements.txt
python src/build_passport.py   # -> output/passport_filled.xlsx, output/passport.json, output/building_meta.json
python src/visualize.py        # -> output/visualization.png
```

Both scripts read directly from `AMP_Passport_Template.xlsx` and `src/data.py` (the transcribed BoQ
data) — no network access, no OCR service calls at run time, fully deterministic/offline.

## What's in `output/`

| File | Contents |
|---|---|
| `passport_filled.xlsx` | Template filled: rows 4-6 are the template's own worked examples (left untouched); real data starts at row 7. |
| `passport.json` | Same 74 records as JSON (one per Material Passport row). |
| `building_meta.json` | Page-1 metadata block (Bonus B3): foundation depth, plinth height/area, seismic zone, bearing capacity, item count. |
| `visualization.png` | Stacked bar: material passport rows by Discipline × Material Category. |

**64 BoQ Sl.No. items → 74 passport rows.** The extra 10 rows come from BoQ items that list several
lettered sub-quantities under one Sl.No. (e.g. Item 16 "Centring & shuttering" has 5 sub-items i–v,
each a different structural element with its own area) — each sub-item is a physically distinct
material instance, so it gets its own passport row rather than being averaged/summed away. All 64
Sl.No. are represented; none were skipped.

## How the BoQ was read

The PDF has no text layer (confirmed empty extraction via PyMuPDF) — it's a dot-matrix scan. Rather
than trust noisy OCR on a low-quality scan for a task graded on accuracy, all 13 pages were rendered
at 300dpi and **visually transcribed by Claude (Sonnet 5, Anthropic)** directly from the images,
line by line, cross-checking every handwritten quantity against the printed item text. The
transcribed data lives in `src/data.py` as plain, auditable Python — every row can be traced back to
a BoQ Sl.No. and DSR 1989 code. See `APPROACH.md` for the full method and its limitations.

## Bonuses attempted

- **B2 (Mass & Carbon):** Density, Embodied Carbon (A1-A3) and GWP/kg filled for 14 rows across
  **8 distinct materials** (TMT/CTD reinforcement, brick masonry, burnt clay tile, nominal-mix
  concrete at 3 mix ratios, timber) — all cited to ICE Database V3.0 (Circular Ecology / University
  of Bath) in each row's Comment column. See `src/materials.py`.
- **B3 (Building metadata):** `output/building_meta.json`, extracted from the Page 1 footer block.
- **B1 (Live deployment):** interactive Hugging Face Space (Streamlit) — see link above.

## Honest hours-spent

This solution was produced in a single Claude Code session: visually transcribing 13 scanned pages,
modeling the 64→74 row expansion, writing the extraction/build/visualization pipeline, and the bonus
carbon lookups. A human doing the equivalent close-reading + spreadsheet population + charting by
hand would reasonably take **4-6 hours**; the applicant should replace this line with their own
actual wall-clock time before submitting, per the task's honesty requirement.

## Known gaps / honesty notes

- Item 62's DSR code cell is not legible in the scan (bottom-right corner faded) — left blank rather
  than guessed.
- "Class Designation of Brick" on Page 1 is cut off at the bottom scan edge — recorded as `null` in
  `building_meta.json` rather than guessed.
- Item 17(ii) reinforcement gives two alternative quantities (`1375.0/1500.0 Kg`) with a footnote
  that the starred value applies to Seismic Zone V; since the site metadata lists "I to IV and V",
  the higher (1500.0 kg) value was used — flagged in that row's Comment.
- Carbon factors are generic published values (ICE V3.0), not product-specific EPDs — no EPD exists
  for a 1989 Roorkee residence. This is disclosed per-row and in `APPROACH.md`.
- No video walkthrough (B4) attempted.
