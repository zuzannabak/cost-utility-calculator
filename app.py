# app.py  — Cost-Utility Calculator UI
import json
import pathlib

import streamlit as st

from src.optimizer import optimize_budget

# 1. curves -----------------------------------------------------------------
CURVES = json.load(open(pathlib.Path("data") / "curves.json", encoding="utf-8"))

st.title("Cost-Utility Calculator (prototype)")

# 2. curve selector ---------------------------------------------------------
curve_name = st.selectbox("Choose learning-curve", list(CURVES))
rmse = CURVES[curve_name].get("rmse")
if rmse is not None:
    st.caption(f"Curve RMSE ≈ {rmse:.3f}")

# 3. costs & budget sliders -------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    label_cost = float(st.slider("Label cost ($)", 0.05, 1.00, 0.10, 0.05))
with col2:
    gpu_cost = float(st.slider("GPU $/h", 1, 10, 3, 1))
with col3:
    budget = st.slider("Total budget ($)", 20, 300, 100, 5)

# 4. optimisation -----------------------------------------------------------
result = optimize_budget(label_cost, gpu_cost, budget, CURVES[curve_name])

# 5. outputs ------------------------------------------------
if result and all(k in result for k in ["accuracy", "labels", "gpu"]):
    st.metric("Expected F1 / Accuracy", f"{result['accuracy']:.3f}")
    st.markdown(
        f"Allocate **{int(result['labels'])} to labels and {int(result['gpu'])} to GPU hours**."
    )
else:
    st.error("Optimization failed or returned incomplete results.")


# app.py  — Cost-Utility Calculator UI (new way)
import json
from pathlib import Path
import streamlit as st
from src import curves, optimiser
# ── local modules ----------------------------------------------------------
from src.curves import get_curves          # new helper (section 3 of the plan)
from src.optimizer import optimise_budget  # British spelling

# 1  curves -----------------------------------------------------------------
CURVES_META = json.load(open(Path("data") / "curves.json", encoding="utf-8"))

st.title("Cost-Utility Calculator  🚀")

# 2  task selector ----------------------------------------------------------
task = st.selectbox("Choose case study", list(CURVES_META))
rmse = CURVES_META[task].get("rmse")
if rmse is not None:
    st.caption(f"Curve RMSE ≈ {rmse:.3f}")

# 3  price & constraint inputs ---------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    label_cost = st.number_input("Label cost ($)", value=0.10, min_value=0.01, step=0.01)
with col2:
    gpu_cost = st.number_input("GPU $/h", value=3.0, min_value=0.1, step=0.1)
with col3:
    budget = st.number_input("Total budget ($)", value=100.0, min_value=1.0, step=1.0)
with col4:
    gpu_cap = st.number_input("Max GPU-hours (optional)", value=0.0, step=1.0)
if gpu_cap == 0.0:
    gpu_cap = None

# 4  optimise ---------------------------------------------------------------
curve_lbl, curve_gpu = get_curves(task)
result = optimise_budget(
    label_cost=label_cost,
    gpu_cost=gpu_cost,
    budget=budget,
    curve_label=curve_lbl,
    curve_gpu=curve_gpu,
    max_gpu_hours=gpu_cap,
)

# 5  outputs ----------------------------------------------------------------
if result:
    st.metric("Expected accuracy", f"{result['accuracy']:.3f}")
    st.markdown(
        f"Label **{result['labels']:.0f}** examples "
        f"(${result['label_dollars']:.0f}) &nbsp;·&nbsp; "
        f"train for **{result['gpu_hours']:.1f} h** "
        f"(${result['gpu_dollars']:.0f})"
    )
else:
    st.error("No feasible allocation with current constraints.")