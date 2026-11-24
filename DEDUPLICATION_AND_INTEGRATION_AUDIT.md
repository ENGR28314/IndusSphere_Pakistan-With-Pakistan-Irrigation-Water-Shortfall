# Deduplication and Integration Audit — 2026-11-24

## Integration
- Added `irrigation_shortfall.py` as a separate module and registered it in `app.py` navigation.
- Preserved all original project modules, datasets, images, source documents, and existing Dam Storage Capacity & CCA Planning content.
- Added README and manifest documentation.

## Duplicate check
- Exact byte-level duplicate groups were detected among three portrait aliases, two dashboard-reference image aliases, and two WAPDA telecommunications PDFs.
- These aliases were retained because distinct paths may be referenced by existing app code, documentation, or user workflows. Removing them without a complete path-reference migration could break existing features.
- No duplicate rows were introduced in the new causes, province, season, solutions, or initiative tables.

## Evidence handling
- User-provided numerical claims (for example 50–60% conveyance loss, 30-day storage, reservoir sedimentation percentages, tubewell counts, seasonal shortage percentages and project targets) are identified as requiring current verification.
- Seasonal calculator defaults are illustrative and editable, not official allocations or measured national demand.
- Efficiency calculations are simplified screening only and explain that reduced diversion does not automatically equal basin-scale water savings because return flows and consumptive use matter.

## Validation
- All Python source files are syntax-compiled in this build.
- ZIP integrity is checked after packaging.
- Streamlit UI/runtime, Streamlit Cloud deployment, and live CrewAI/provider calls are not claimed as tested because Streamlit is not installed in the build container.


## 2026-11-24 Indus Plain comparison-table hotfix
- Corrected three rows in the Upper versus Lower Indus Plain comparison table that had been expressed as Python sets instead of dictionaries.
- Standardized all comparison rows to `Feature`, `Upper`, and `Lower` fields and supplied explicit DataFrame columns.
- Checked the full `app.py` AST for set literals nested in `pandas.DataFrame` calls; none remain.
- Executed the repaired five-row table construction successfully with pandas.
