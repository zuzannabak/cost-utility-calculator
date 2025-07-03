# app.py  — Cost-Utility Calculator UI
import json, pathlib, streamlit as st
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
    gpu_cost   = float(st.slider("GPU $/h",        1,    10,   3,     1))
with col3:
    budget     =        st.slider("Total budget ($)", 20, 300, 100, 5)

# 4. optimisation -----------------------------------------------------------
result = optimize_budget(label_cost, gpu_cost, budget, CURVES[curve_name])

# 5. outputs ------------------------------------------------
if result and all(k in result for k in ['accuracy', 'labels', 'gpu']):
    st.metric("Expected F1 / Accuracy", f"{result['accuracy']:.3f}")
    st.markdown(
        f"Allocate **{int(result['labels'])} to labels and {int(result['gpu'])} to GPU hours**."
    )
else:
    st.error("Optimization failed or returned incomplete results.")
