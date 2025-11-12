"""
Streamlit front-end for the Cost-Utility Calculator.
"""

import json
from pathlib import Path

import streamlit as st
from cucal.curves import get_curves
from cucal.optimizer import optimise_budget
from cucal.hardware import load_hardware, calculate_energy, co2_equivalent
from cucal.config import DEFAULT_CLUSTER_EFF

# -----------------------------  Layout & title  ----------------------------#
st.set_page_config(page_title="Cost-Utility Calculator", page_icon="🚀")
st.title("Cost-Utility Calculator 🚀")

# -------------------------  Case-study selection  -------------------------#
META = json.loads((Path("data") / "curves.json").read_text())
BASES = sorted({k.rsplit("-", 1)[0] for k in META})
task = st.selectbox("Choose case study", BASES)

# show RMSE for the *label* curve (if present)
rmse_entry = META.get(f"{task}-label", {}) or META.get(f"{task}-gpu", {})
rmse_value = rmse_entry.get("rmse", 0.02)
if rmse_entry.get("rmse") is not None:
    st.caption(f"Curve RMSE ≈ {rmse_value:.3f}")

# -----------------------------  Input controls  ----------------------------#
c1, c2, c3, c4 = st.columns(4)

with c1:
    label_cost_hour = st.number_input("Labels $/h", min_value=0.0, value=8.0)
    gamma = st.slider("γ (instances / hour)", 1, 30, 20)
    # Convert to per-instance cost for the optimiser
    label_cost_instance = label_cost_hour / gamma if gamma > 0 else 0.0

with c2:
    gpu_cost = st.number_input("GPU $/h", 0.10, value=3.00, step=0.10)

with c3:
    budget = st.number_input("Total budget ($)", 1.0, value=100.0, step=1.0)

mode = st.radio(
    "Objective",
    ["Maximise accuracy", "Hit accuracy target ↗"],
    horizontal=True,
)

target_acc = None
if mode == "Hit accuracy target ↗":
    target_acc = st.number_input("Desired accuracy (0–1)", 0.50, 1.00, 0.90, 0.005)

with c4:
    gpu_cap = st.number_input(
        "Max GPU-hours",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="0 = no limit",
    )
gpu_cap = None if gpu_cap == 0 else gpu_cap

st.subheader("⏱ Time constraints")
col5, col6 = st.columns(2)

with col5:
    wall_limit = st.slider("Time budget (h)", 0, 168, 0, 1, help="0 = no limit")
    wall_limit = None if wall_limit == 0 else float(wall_limit)

with col6:
    efficiency_pct = st.slider(
        "Cluster efficiency (%)", 10, 100, int(100 * DEFAULT_CLUSTER_EFF), 1
    )

# ---------------------------  Run optimisation  ---------------------------#
curve_lbl, curve_gpu = get_curves(task)

res = optimise_budget(
    label_cost=label_cost_instance,
    gpu_cost=gpu_cost,
    budget=budget,
    curve_label=curve_lbl,
    curve_gpu=curve_gpu,
    label_rmse=rmse_value,
    gamma=gamma,
    max_gpu_hours=gpu_cap,
    wall_clock_limit_hours=wall_limit,
    cluster_efficiency_pct=efficiency_pct,
    target_accuracy=target_acc,
)

# ---------------------------  Display results  ----------------------------#
if res is None:
    st.warning("⚠️  No feasible allocation. Increase budget or relax caps.")
    st.stop()

# --- define values from the result dict ---
mean = res["accuracy"]
lo, hi = res["accuracy_ci"]
label_hours = (res["labels"] / gamma) if gamma > 0 else 0.0

# If user set a target, tell them whether we reach it (UI-only)
if target_acc is not None:
    if mean < target_acc:
        st.warning(
            f"⚠️  With budget ${budget:.0f}, best achievable accuracy is "
            f"{mean:.3f}, below the target {target_acc:.3f}."
        )
    else:
        st.success(f"Target {target_acc:.3f} is achievable (best ≈ {mean:.3f}).")

st.metric(
    "Expected accuracy",
    f"{mean:.3f}",
    help=f"95 % CI: {lo:.3f} – {hi:.3f}",
)


st.markdown(
    f"""
<div style='background:#1e1e1e;padding:1em;border-radius:8px;'>
<ul style='list-style-type:none;padding-left:0;color:#ddd;font-size:0.95em;'>

  <li><b>Label:</b> {res['labels']:.0f} (≈ {label_hours:.1f} h)
      <span style='color:#999;'>(${res['label_dollars']:.0f})</span></li>

  <li><b>Annotate:</b> {label_hours:.1f} h&nbsp;|&nbsp;
      <b>Train:</b> {res['gpu_hours']:.1f} GPU-h
      <span style='color:#999;'>(${res['gpu_dollars']:.0f})</span></li>

  <li><b>Wall-clock:</b> {res['wall_clock_hours']:.1f} h&nbsp;@&nbsp;{efficiency_pct}%</li>
</ul>
</div>
""",
    unsafe_allow_html=True,
)

st.download_button(
    "📋 Copy plan as JSON",
    data=json.dumps(res, indent=2),
    file_name=f"{task.lower()}_plan.json",
    mime="application/json",
)

time_arg = f"--time {int(wall_limit)} " if wall_limit else ""
cli_snippet = (
    f"python -m cucal --budget {budget} "
    f"{time_arg}--eff {efficiency_pct} {task}"
)
st.code(cli_snippet, language="bash")

# -------------------------------  ENERGY  ----------------------------------#
st.header("Energy usage")

hardware_db = load_hardware()
gpu_names = list(hardware_db.keys())

col7, col8 = st.columns(2)
with col7:
    selected_gpu = st.selectbox(
        "Choose hardware:",
        gpu_names,
        index=0,
        help="Power rating from hardware.json",
    )
with col8:
    gpu_hours = st.number_input("GPU-hours:", 0.0, step=0.25, value=1.0)

co2_grid = st.slider(
    "Grid carbon intensity (g CO₂ / kWh)",
    min_value=100,
    max_value=800,
    value=450,
    step=10,
)

if st.button("Compute energy"):
    power = hardware_db[selected_gpu]["power"]  # W
    energy = calculate_energy(power, gpu_hours)  # Wh
    
    co2 = co2_equivalent(energy, co2_grid)
    st.success(
        f"**Energy:** {energy:,.0f} Wh  |  "
        f"**Footprint:** {co2:,.0f} g CO₂"
    )
