# Cost-Utility Calculator for NLP Model Development

Economic decision-support tool that recommends how to split a fixed budget
between **knowledge-distillation compute** and **human annotation** when fine-tuning
compact NLP models.

## Key Features
- 💸 **Cost/utility optimiser** – chooses the best split of dollars between GPUs and labels.  
- 📈 **Interactive curves** – visualise marginal utility & diminishing returns.  
- 🕒 **Time-budget constraint (NEW, Week 4)** – slider lets you cap total wall-clock hours; simulator prunes solutions that exceed it.  
- 🌳 *Optional* **CO₂ tracker** – estimate carbon for each configuration.

## Project Goals
1. Formalise the allocation problem with marginal-utility economics.
2. Build a lightweight simulation (Python) that takes user-entered costs and
   outputs the optimal budget mix, expected accuracy, time, and optional CO₂.
3. Validate on two case studies: regex-style entity extraction & RL summarisation.

## Folder Structure
📁 notebooks/ – Jupyter prototypes and analysis  
📁 src/ – reusable Python modules  
📁 data/ – small sample datasets (keep < 10 MB)  
📁 docs/ – figures, literature-review matrix  
requirements.txt – Python dependencies

---

## Quick Start (local)

```bash
git clone https://github.com/<zuzannabak/cost-utility-calculator.git
cd cost-utility-calculator

# ----- create env & install -----
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]          # editable install; add extras as needed


# Conda
conda create -n cucal python=3.11
conda activate cucal
pip install -r requirements.txt

# or with plain venv + pip
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt


### Run the simulator (Streamlit)

streamlit run streamlit_app.py

Then open the browser tab that Streamlit launches and:

  • Move the **Label-Cost ($)** and **GPU-Cost ($)** sliders to match your scenario.  
  • Set **Budget ($)** and (optionally) **Time Budget (h)**.  
  • Read off the recommended split and expected utility.


### Run from the CLI

python -m cost_utility_calculator \
  --task dragut_2019 \
  --label-cost 0.07 \
  --gpu-cost 1.50 \
  --budget 3000 \
  --max-gpu-hours 800 \
  --wall-clock-limit 72      # cap run-time at 72 h

The script prints the optimal allocation and metadata as JSON.

---

## Roadmap
 **Week 0** – confirm abstract; register independent study  ✔  
 **Week 1** – literature-review matrix + first prototype curves  ✔  
 **Week 2** – fit cost/utility curves to data  ✔  
 **Week 3** – implement constrained optimisation routine  ✔  
 **Week 4** – minimal Streamlit (or CLI) front-end (prototype simulator)  ✔ (CLI)  
 **Week 5** – validate on Dragut entity-extraction case  ✔ (WIP ~70%)  
 **Week 6** – generalize to summarisation case & refine simulator  
 **Week 7** – draft report, polish plots, add tests  
 **Week 8** – final demo + 6–8 page report  

**(Timeline is optimistic; project spans the full 12-week summer term.)**

---

## References
Dragut E. C. et al. (2019) How to Invest My Time: Lessons from Human-in-the-Loop Entity Extraction. KDD.

Kang J., Xu W., & Ritter A. (2023) Distill or Annotate? Cost-Efficient Fine-Tuning of Compact Models. arXiv:2305.01645.

Stiennon N. et al. (2021) Learning to Summarize with Human Feedback. EMNLP.
