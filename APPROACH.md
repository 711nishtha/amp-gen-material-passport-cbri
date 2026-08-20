# APPROACH

## Tools picked, and why

- **Vision-based manual transcription over OCR.** The scan has no text layer (PyMuPDF returns empty
  strings on every page) and is a low-contrast dot-matrix printout with handwritten quantities,
  smudges, and a torn/creased edge on Page 1. A quick Tesseract test on a sample page produced
  garbled numbers on exactly the column that matters most (quantity) — the worst possible place for
  an OCR error on a task graded on accuracy. Instead, all 13 pages were rendered at 300dpi with
  PyMuPDF and read visually, item by item, cross-checking each handwritten quantity figure against
  the printed unit and DSR code. This is slower than OCR but auditable: every value in `src/data.py`
  traces back to a specific page/line, and mistakes are transcription errors I can be pointed at,
  not opaque model hallucinations from a noisy pipeline.
- **openpyxl** to write directly into the provided template (preserves formatting/colour-coding,
  no risk of a re-derived schema drifting from the original).
- **Plain Python dict/list data** (`src/data.py`) instead of an intermediate CSV — kept the raw
  transcription, the sub-item expansion logic, and the unit-normalization in one reviewable place.
- **matplotlib** for the chart — no external chart service, deterministic output, no extra runtime
  dependency (avoided plotly+kaleido to keep `pip install` under a minute).

## What worked

- The DSR 1989 code (rightmost column) gave a reliable secondary check on category classification
  even where the item description was ambiguous — chapter 2.x is consistently earthwork, 4.x plain
  concrete, 5.x RCC, 6.x brickwork, 9.x joinery/hardware, 11-13.x finishes, matching the sub-head
  convention already implied by the template's own example rows.
- Treating "64 line items" as 64 Sl.No. entries (not 64 output rows) resolved the only structural
  ambiguity in the brief: several Sl.No. list multiple lettered sub-quantities (different elements,
  different areas/weights) under one description. Expanding those to one row per sub-item (64 → 74
  rows) keeps each row physically meaningful instead of forcing a lossy merge.
- Cross-referencing the template's *own* worked examples (rows 4-6) resolved several schema
  ambiguities the Instructions sheet leaves implicit: Grade/Mix-Ratio are largely left blank even
  where the mix is known (folded into the Material/Product name and Classification string instead),
  and the "BOQ Item No." vs "Schedule Item Code" split maps to Sl.No. vs DSR code respectively.

## What didn't work / had to be judgment calls

- **Item 62's DSR code** and the **"Class Designation of Brick" value on Page 1** are genuinely not
  legible in the scan (faded ink / page cut off at the physical edge of the source document, not a
  rendering issue) — left blank/`null` rather than invented.
- **Discipline assignment** (Structural vs Architectural) for brick masonry and metalwork items is a
  judgment call where DSR text alone doesn't disambiguate load-bearing vs partition/fenestration use
  — flagged as such rather than presented as certain.
- **Mass & Carbon (bonus)** values are generic ICE Database V3.0 factors, not product EPDs — none
  exist for 1989-era materials at this site. Embodied carbon (absolute kg CO2e) was only computed
  where both a density factor *and* a real mass basis existed (volume directly, or area × known
  thickness); rows without a defensible mass basis got Density/GWP-per-kg only, left the absolute
  carbon figure blank rather than guess a thickness.
- **Rate/Amount** (DSR columns 4 and 6) are blank throughout the entire scanned BoQ — Unit Rate,
  Total Cost and Currency were left blank rather than fabricated.

## With 2 more weeks

- Replace the visual transcription with a proper human-in-the-loop OCR pass (Google Document AI or
  Azure Form Recognizer table mode) and diff it against this transcription to catch any remaining
  misreads — the two-source cross-check is worth more than either source alone on a scan this poor.
- Source real EPDs for the dominant materials (Indian fired-clay brick, TMT rebar from a named mill)
  via GreenPro/CII-Godrej GBC data instead of generic ICE factors.
- Build the Circularity/Detachability/Lifespan (grey) columns properly — they were out of scope here,
  but a 1989 brick-and-RCC residence is actually a reasonable case study for reuse potential (lime
  mortar/masonry salvage, TMT rebar recovery) that a real Madaster-style assessment would want.
- Add a second chart: total embodied carbon by discipline (weight-based rather than item-count-based),
  once real EPDs make that number trustworthy across all rows, not just the 8 materials covered here.
