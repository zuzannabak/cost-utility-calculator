import json
import pathlib
import streamlit as st
from src.optimizer import optimize_budget

# -----------------------------------------------------------
# 1. load all fitted curves once at startup
# -----------------------------------------------------------
CURVES = json.load(open(pathlib.Path("data") / "curves.json"))

st.title("Cost-Utility Calculator (prototype)")

# -----------------------------------------------------------
# 2. curve selector (+ optional RMSE caption)
# -----------------------------------------------------------
curve_name = st.selectbox("Choose learning-curve", list(CURVES))

rmse = CURVES[curve_name].get("rmse")      # returns None if key absent
if rmse is not None:
    st.caption(f"Curve RMSE ≈ {rmse:.3f}")

# -----------------------------------------------------------
# 3. user-controlled costs and total budget
# -----------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    label_cost = st.slider("Label cost ($)", 0.05, 1.00, 0.10, 0.05)
with col2:
    gpu_cost   = st.slider("GPU $/h",        1,    10,    3,     1)
with col3:
    budget     = st.slider("Total budget ($)", 20, 300, 100, 5)

# -----------------------------------------------------------
# 4. optimisation
# -----------------------------------------------------------
params = CURVES[curve_name]
result = optimize_budget(label_cost, gpu_cost, budget, params)

# -----------------------------------------------------------
# 5. outputs
# -----------------------------------------------------------
st.metric("Expected F1 / Accuracy", f"{result['accuracy']:.3f}")

st.markdown(
    f"Allocate **${result['labels']}** to labels and "
    f"**${result['gpu']}** to GPU hours."
)
