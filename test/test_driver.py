from molecule.config import molecule_drivers


def test_driver_is_detected():
    assert "azure" in molecule_drivers()
