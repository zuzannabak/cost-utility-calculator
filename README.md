# Cost–Utility Calculator for NLP Model Development

An interactive Python tool for optimizing how to allocate a fixed budget between **data labeling**, **GPU compute**, and other resources when fine-tuning compact NLP models.  
Implements cost-utility curves from recent papers and recommends efficient configurations under accuracy, time, and energy constraints.

## Overview

This tool models the trade-off between human annotation and compute cost in machine learning.  
It uses saturating-log accuracy curves fitted to literature data (Dragut 2019; Kang 2023; Stiennon 2021) and performs exhaustive or gradient-based search to recommend optimal spending strategies.

## Key Features
- **Budget optimizer** for multiple resources (labels, GPU, dev effort).  
- **Time and CO₂ constraints** integrated into the model.  
- **Curve fitting** based on real research datasets.  
- **Two interfaces:** Streamlit GUI & Python CLI.  
- **Configurable JSON inputs** for adding new tasks.  
- **Unit-tested** and easily extensible.

## Quick Start

```bash
git clone https://github.com/zuzannabak/cost-utility-calculator.git
cd cost-utility-calculator
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Launch GUI

```bash
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) to explore.

## Run from CLI
```bash
python -m cucal.cli \
  --task dragut_2019 \
  --budget 3000 \
  --label-cost 0.07 \
  --gpu-cost 1.50 \
  --max-gpu-hours 800
```

## Repositry Layout
```bash
.
├─ src/cucal/       # Core modules: optimizer, curves, config, CLI
├─ data/            # Curve and resource configs
├─ docs/            # Figures, screenshots, paper notes
├─ notebooks/       # Validation & prototypes
├─ tests/           # Unit tests
├─ app.py           # Streamlit entry point
└─ report.pdf       # Final report / summary
```

## Example Screenshot

(optional – place in docs/ui-preview.png)

## References

* Dragut et al., Human-in-the-Loop Entity Extraction (KDD 2019)
* Kang et al., Distill or Annotate? Cost-Efficient Fine-Tuning (2023)
* Stiennon et al., Learning to Summarize with Human Feedback (EMNLP 2021)

## Author
Zuzanna Bąk
M.S. Computational Data Science, Temple University
zuzanna.bak@temple.edu
