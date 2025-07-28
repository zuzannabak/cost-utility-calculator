from cucal.hardware import calculate_energy
from cucal.hardware import co2_equivalent


def test_calculate_energy():
    assert calculate_energy(400, 2.5) == 1000.0  # 400 W × 2.5 h = 1 000 Wh

def test_energy_and_co2():
    wh = calculate_energy(power_w=400, gpu_hours=2.5)
    assert wh == 1000.0
    g = co2_equivalent(wh, gco2_per_kwh=450)
    assert g == 450.0