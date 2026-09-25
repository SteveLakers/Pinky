# Walk-Forward Results (v2 prep)

Date: 2026-09-23  
Focus: **1y horizon**  
Changes vs v1:
1. Cross-sectional z-score by day (“grade on a curve”)
2. Dropped highly correlated features (31 → **11**)
3. Focused on 1y
4. Ridge kept as baseline to beat
5. Smaller / more regularized LightGBM

## Verdict

**Soft bar vs Ridge: still FAIL / MIXED**  
- Rank IC: LightGBM **beats** Ridge (0.122 vs 0.108; wins **88%** of folds)  
- Top-5 basket: LightGBM slightly **behind** Ridge (0.425 vs 0.434; wins **62%** of folds)

## vs v1 (1y)

| Metric | v1 LightGBM | v2 LightGBM | v2 Ridge |
|--------|-------------|-------------|----------|
| Mean IC | 0.119 | **0.122** | 0.108 |
| IC win vs Ridge | 50% | **88%** | — |
| Mean top-5 excess | 0.368 | **0.425** | 0.434 |
| Universe top-5 ref | 0.050 | 0.050 | 0.050 |

## Takeaway

Prep helped a lot on ranking skill. Top-5 still not clearly better than Ridge, so we do **not** claim pass yet.

Next likely levers: refine top-N rule, try ElasticNet, or mild feature adds that are stock-specific (not more macros).
