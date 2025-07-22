from src.cucal.hardware import calculate_energy

def test_calculate_energy():
    assert calculate_energy(400, 2.5) == 1000.0  # 400 W × 2.5 h = 1 000 Wh
