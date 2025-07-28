# Literature Curve Estimate

This document explains how the estimate of literature with usable cost–utility curves was computed.

## Goal
Estimate how many published papers (2015–2025) contain **performance vs. cost trade-off curves** (labeling cost, GPU/compute time, energy, etc.) in **supervised learning or NLP**.

## Sampling Summary

- **Papers reviewed**: 25
- **Papers with extractable curves**: 12  
  → Curve ratio: `12 / 25 = 0.48`

## Total Domain Size

Using queries such as:
> "active learning" AND "budget" AND ("label" OR "gpu") AND ("accuracy" OR "performance")

Total estimated relevant papers in domain: ~1200 (from Semantic Scholar & Google Scholar filters).

## Final Estimate

\[
0.48 	imes 1200 = oxed{576}
\]

Roughly **576 papers** from 2015–2025 are estimated to contain usable empirical curves suitable for:
- Re-fitting accuracy vs. label/compute cost curves
- CO₂ or energy-aware trade-off analysis
- Future ML training for predictive allocation modeling

## Use

This estimate supports:
- Scope definition for future **curve dataset mining**
- Planning a pipeline to digitize, store, and model from literature
- ML simulation models trained on paper-derived utility functions

> Estimate is stored in `lit_stats.json`.
