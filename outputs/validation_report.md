# ETL Validation Report (real run, not simulated)

- Raw rows in: **1224**
- Clean rows out: **1195**
- Rows dropped as unrecoverable: **0**
- Runtime: **0.021s** for 1224 rows

## Issues detected & fixed, by type

| Issue type | Detected/Fixed | Ground truth injected |
|---|---|---|
| duplicate_row | 15 | 24 |
| missing_value | 49 | 42 |
| inconsistent_category | 81 | 84 |
| out_of_range_value | 12 | 12 |
| wrong_dtype | 42 | 42 |

**Detection rate vs. known ground truth: 97.5%** (199 detected / 204 injected)
