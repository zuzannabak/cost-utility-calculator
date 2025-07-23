"""
Streamlit front-end for the Cost-Utility Calculator.
"""

import json
from pathlib import Path

import streamlit as st

from cucal.curves import get_curves
from cucal.optimizer import optimise_budget
from cucal.hardware import load_hardware, calculate_energy

# -----------------------------  Layout & title  ----------------------------#
st.set_page_config(page_title="Cost-Utility Calculator", page_icon="🚀")
st.title("Cost-Utility Calculator 🚀")

# -----------------------------  Case-study curves  -------------------------#
META  = json.loads((Path("data") / "curves.json").read_text())
BASES = sorted({k.rsplit("-", 1)[0] for k in META})        # Dragut-2019, …
task  = st.selectbox("Choose case study", BASES)

# show RMSE for the *label* curve (if present)
rmse_entry = META.get(f"{task}-label", {}) or META.get(f"{task}-gpu", {})
if (rmse := rmse_entry.get("rmse")):
    st.caption(f"Curve RMSE ≈ {rmse:.3f}")

# ------------------------------  Inputs pane  -----------------------------#
c1, c2, c3, c4 = st.columns(4)
with c1:
    label_cost = st.number_input(
        "Label cost ($)",
        min_value=0.01,
        value=0.10,
        step=0.01,
    )

with c2:
    gpu_cost = st.number_input(
        "GPU $/h",
        min_value=0.10,
        value=3.00,
        step=0.10,
    )

with c3:
    budget = st.number_input(
        "Total budget ($)",
        min_value=1.0,
        value=100.0,
        step=1.0,
    )

with c4:
    gpu_cap = st.number_input(
        "Max GPU-h (0 = none)",
        min_value=0.0,
        value=0.0,
        step=1.0,
    )
if gpu_cap == 0:
    gpu_cap = None

# -----------------------  New time-budget controls  ------------------------#
st.subheader("⏱ Time constraints")
col5, col6 = st.columns(2)
with col5:
    wall_limit = st.slider(
        "Time budget (hours)",
        min_value=0,
        max_value=168,
        value=0,
        step=1,
        help="0 means no limit",
    )
    wall_limit = None if wall_limit == 0 else float(wall_limit)

with col6:
    efficiency_pct = st.slider(
        "Cluster efficiency (%)",
        min_value=10,
        max_value=100,
        value=60,
        step=1,
    )

# ---------------------------  Run optimisation  ---------------------------#
curve_lbl, curve_gpu = get_curves(task)
res = optimise_budget(
    label_cost=label_cost,
    gpu_cost=gpu_cost,
    budget=budget,
    curve_label=curve_lbl,
    curve_gpu=curve_gpu,
    max_gpu_hours=gpu_cap,
    wall_clock_limit_hours=wall_limit,
    cluster_efficiency_pct=efficiency_pct,
)

# ---------------------------  Display results  ----------------------------#
if res is None:
    st.warning("⚠️ No feasible allocation. Increase budget or relax caps.")
else:
    lo, hi = res["accuracy_ci"]
    ci_txt = f"95 % CI: {lo:.3f} – {hi:.3f}"
    st.metric("Expected accuracy", f"{res['accuracy']:.3f}", help=ci_txt)

    st.markdown(
        f"""
<div style='background-color:#222;padding:1em;border-radius:8px;'>
<ul style='list-style-type:none;padding-left:0;color:#ddd;'>
  <li><b>Label:</b> <span style='font-size:1.2em;'>{res['labels']:.0f}</span>
      examples <span style='color:#999;'>(${res['label_dollars']:.0f})</span></li>
  <li><b>Train:</b> <span style='font-size:1.2em;'>{res['gpu_hours']:.1f}</span>
      GPU-h <span style='color:#999;'>(${res['gpu_dollars']:.0f})</span></li>
  <li><b>Wall-clock:</b> <span style='font-size:1.2em;'>{res['wall_clock_hours']:.1f}</span>
      h @ {efficiency_pct}% efficiency</li>
</ul>
</div>
""",
        unsafe_allow_html=True,
    )

# -------------------------------  ENERGY  ----------------------------------#
st.header("Energy usage")

hardware_db = load_hardware()  # {'A100': {'power': 400}, ...}
gpu_names = list(hardware_db.keys())

col7, col8 = st.columns(2)
with col7:
    selected_gpu = st.selectbox(
        "Choose hardware:",
        gpu_names,
        index=0,
        help="Power rating taken from hardware.json",
    )
with col8:
    gpu_hours = st.number_input(
        "GPU-hours:",
        min_value=0.0,
        step=0.25,
        value=1.0,
        help="Wall-clock hours × #GPUs",
    )

if st.button("Compute energy"):
    power = hardware_db[selected_gpu]["power"]  # [W]
    energy = calculate_energy(power, gpu_hours)  # [Wh]
    st.success(f"**Energy used:** {energy:,.0f} Wh")
