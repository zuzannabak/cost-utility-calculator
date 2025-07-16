"""
Streamlit front-end for the Cost-Utility Calculator.
"""
import json
from pathlib import Path
import streamlit as st
from src.curves import get_curves
from src.optimizer import optimise_budget

st.set_page_config(page_title="Cost-Utility Calculator", page_icon="🚀")
st.title("Cost-Utility Calculator 🚀")

META = json.loads((Path("data") / "curves.json").read_text())
task = st.selectbox("Choose case study", list(META))
if (rmse := META[task].get("rmse")): st.caption(f"Curve RMSE ≈ {rmse:.3f}")

c1,c2,c3,c4 = st.columns(4)
with c1: label_cost = st.number_input("Label cost ($)",
                             min_value=0.01,  # smallest allowed
                             value=0.10,      # default shown
                             step=0.01)

with c2: gpu_cost   = st.number_input("GPU $/h",
                             min_value=0.10,
                             value=3.00,
                             step=0.10)

with c3: budget     = st.number_input("Total budget ($)",
                             min_value=1.0,
                             value=100.0,
                             step=1.0)

with c4: gpu_cap    = st.number_input("Max GPU-h (0 = none)",
                             min_value=0.0,
                             value=0.0,
                             step=1.0)
if gpu_cap==0: gpu_cap=None

curve_lbl, curve_gpu = get_curves(task)
res = optimise_budget(
    label_cost=label_cost, gpu_cost=gpu_cost, budget=budget,
    curve_label=curve_lbl, curve_gpu=curve_gpu, max_gpu_hours=gpu_cap
)


if res is None:
    st.warning("⚠️ No feasible allocation. Increase budget or relax GPU-hour cap.")
else:
    st.metric("Expected accuracy", f"{res['accuracy']:.3f}")
    st.write(
        f"Label **{res['labels']:.0f}** examples "
        f"(${res['label_dollars']:.0f}) — "
        f"train **{res['gpu_hours']:.1f} h** "
        f"(${res['gpu_dollars']:.0f})"
        )