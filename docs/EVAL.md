# Pinky Eval Checklist (v1)

Use this before calling a model “good.” Do **not** trust a single accuracy number.

## Must-pass rules

- [ ] Walk-forward only (no random train/test shuffle)
- [ ] Purge overlapping label windows between train and test
- [ ] Report separately for each horizon: 3m / 6m / 1y / 2y
- [ ] Report both heads: excess-return model and beat-SPY model
- [ ] No peeking: test dates only use features available on/before that date

## Metrics to report

### Ranking quality
- [ ] Rank IC / Spearman: predicted excess vs realized excess (per test fold)
- [ ] Top-decile hit rate: do top predicted names actually beat SPY more often?

### Basket vs SPY
- [ ] Equal-weight top-N predicted basket excess vs SPY over the horizon
- [ ] Compare to equal-weight all-universe basket (sanity baseline)

### Probability calibration (beat model)
- [ ] Reliability: when model says ~70% beat chance, do ~70% actually beat?
- [ ] Brier score (lower is better)

### Honesty checks
- [ ] Beat-rate in test set near ~50% (not 80%+ mega-cap bias)
- [ ] Results stable across folds (not one lucky period)
- [ ] Linear baseline included — LightGBM must beat a simple linear model meaningfully

## Fail conditions (do not ship / do not trust)

- Random split used
- Huge score with no purge on overlapping labels
- Only accuracy reported, no ranking/basket/calibration
- Model loses to “always pick recent winners” or linear baseline by a lot

## Pass bar (first useful prototype)

- Beats linear baseline on rank IC **and** top-basket excess in most folds
- Beat probabilities not wildly miscalibrated
- No single fold drives the whole story
