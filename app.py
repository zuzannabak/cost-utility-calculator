"""
Streamlit front-end for the Cost-Utility Calculator.
"""
import json
from pathlib import Path

import streamlit as st

# ── local modules -----------------------------------------------------------
from src.curves import get_curves
from src.optimizer import optimise_budget

# 1  load curve metadata (for RMSE display) ----------------------------------
CURVES_META = json.loads((Path("data") / "curves.json").read_text())

st.set_page_config(page_title="Cost-Utility Calculator", page_icon="🚀")
st.title("Cost-Utility Calculator 🚀")

# 2  case-study selector -----------------------------------------------------
task = st.selectbox("Choose case study", list(CURVES_META))
if (rmse := CURVES_META[task].get("rmse")) is not None:
    st.caption(f"Curve RMSE ≈ {rmse:.3f}")

# 3  user inputs -------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    label_cost = st.number_input("Label cost ($)", value=0.10, min_value=0.01, step=0.01)
with col2:
    gpu_cost = st.number_input("GPU $/h", value=3.0, min_value=0.10, step=0.10)
with col3:
    budget = st.number_input("Total budget ($)", value=100.0, min_value=1.0, step=1.0)
with col4:
    gpu_cap = st.number_input("Max GPU-hours (optional)", value=0.0, step=1.0)
if gpu_cap == 0.0:
    gpu_cap = None  # treat 0 as “no cap”

# 4  optimisation ------------------------------------------------------------
curve_lbl, curve_gpu = get_curves(task)
result = optimise_budget(
    label_cost=label_cost,
    gpu_cost=gpu_cost,
    budget=budget,
    curve_label=curve_lbl,
    curve_gpu=curve_gpu,
    max_gpu_hours=gpu_cap,
)

# 5  outputs -----------------------------------------------------------------
if result is None:
    st.warning(
        "⚠️ No feasible allocation with these constraints. "
        "Increase the budget or relax the GPU-hour cap."
    )
else:
    st.metric("Expected accuracy", f"{result['accuracy']:.3f}")
    st.markdown(
        f"Label **{result['labels']:.0f}** examples "
        f"(${result['label_dollars']:.0f}) — "
        f"train for **{result['gpu_hours']:.1f} h** "
        f"(${result['gpu_dollars']:.0f})"
    )
