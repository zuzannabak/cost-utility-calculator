# Cost–Utility Calculator for NLP Model Development

Economic decision-support tool that recommends how to split a fixed budget
between **knowledge-distillation compute** and **human annotation** when fine-tuning
compact NLP models.

---

## 🔧 Key Features

- 💸 **Cost/utility optimiser** – compute the best allocation of dollars across multiple resources: labels, GPU, dev time.
- 📈 **Diminishing-return curve fitting** – supports log-saturation accuracy curves from real papers (Dragut, Kang, Stiennon).
- 📊 **k-resource support (NEW)** – generalised optimiser allows >2 dimensions (e.g., tool-build, expert effort).
- 🕒 **Time-budget constraint** – slider enforces wall-clock caps.
- 🌍 **CO₂ calculator** – estimates carbon footprint from GPU-hours using region-specific grid intensity.
- 🐚 **CLI + Streamlit GUI** – reproducible simulations via CLI or web sliders.
- 📋 **Exportable results** – JSON plan + CLI snippet generated for each run.
- ✅ **Tests + CI** – 14+ Pytest files, flake8 linter, and GitHub Actions CI.

---

## 🎯 Project Goals

1. Formalise the budget allocation problem under diminishing-return curves.
2. Build an extensible simulator that outputs optimal mixes under cost, time, and energy constraints.
3. Validate with multiple case-studies (entity extraction, RLHF summarisation).
4. Lay groundwork for future meta-models that learn utility functions from research papers.

---

## 📂 Folder Structure

📁 notebooks/ – prototypes, validation notebooks  
📁 src/ – simulator modules (`optimizer.py`, `resource.py`, etc.)  
📁 data/ – cost/unit tables, curves.json, resources.json  
📁 docs/ – literature scan, figures, README artefacts  
📁 tests/ – Pytest validations for optimiser and simulation

---

## 🚀 Quick Start (local)

```bash
git clone https://github.com/zuzannabak/cost-utility-calculator.git
cd cost-utility-calculator

# --- Set up environment ---
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]  # with extras
```

Or using Conda:

```bash
conda create -n cucal python=3.11
conda activate cucal
pip install -r requirements.txt
```

### ▶️ Run GUI

```bash
streamlit run app.py
```

Then:
- Adjust label/GPU cost sliders
- Set total budget + (optional) time limit
- Export JSON result or copy CLI snippet

---

### 🖥️ Run from CLI

```bash
python -m cost_utility_calculator \
  --task dragut_2019 \
  --budget 3000 \
  --label-cost 0.07 \
  --gpu-cost 1.50 \
  --max-gpu-hours 800 \
  --wall-clock-limit 72
```

Returns optimal split + expected accuracy + utility.

---

## 📚 Literature Meta-Estimate

A semi-automated scan using ScholarGPT + Semantic Scholar reveals:

- 12/25 sampled papers include usable cost/accuracy curves.
- Estimated ~576 papers (2015–2025) include such plots.
- See `docs/lit_candidates.md` + `lit_stats.json`.

These curves can be used for:
- Refitting new cost/utility functions
- Training ML models to generalise trade-offs

---

## 📅 Roadmap (Done ✅)

- ✅ Week 0–1: Abstract + curve prototypes + literature matrix
- ✅ Week 2–3: Optimiser implemented for 2D
- ✅ Week 4–5: GUI + JSON/CLI export; Dragut validation (70%)
- ✅ Week 6: Multi-resource generalisation + CO₂ module
- ✅ Week 7: Validation tests, paper estimate, k-resource unit tests
- 🔜 Week 8: Report writing + demo prep

---

## 📖 References

- Dragut et al. (2019). *Human-in-the-Loop Entity Extraction*. KDD.  
- Kang et al. (2023). *Distill or Annotate? Cost-Efficient Fine-Tuning*. arXiv:2305.01645  
- Stiennon et al. (2021). *Learning to Summarize with Human Feedback*. EMNLP  

---

Built with 💡 for research reproducibility and sustainability.

