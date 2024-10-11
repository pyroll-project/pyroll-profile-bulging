import logging
import webbrowser
from pathlib import Path
from pyroll.core import Profile, Roll, ThreeRollPass, Transport, FlatGroove, PassSequence


def test_solve_3rp_round_flat_flat(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.profile_bulging

    in_profile = Profile.round(
        diameter=96e-3,
        temperature=1200 + 273.15,
        strain=0,
        material=["C45", "steel"],
        flow_stress=100e6,
        length=1,
        density=7.5e3,
        specific_heat_capacity=690,
        thermal_conductivity=23
    )

    sequence = PassSequence([
        ThreeRollPass(
            label="Stand - I",
            orientation="Y",
            roll=Roll(
                groove=FlatGroove(
                    r1=5e-3,
                    usable_width=90e-3,
                    pad_angle=30,
                ),
                nominal_radius=293e-3 / 2,
                rotational_frequency=1.73,
            ),
            inscribed_circle_diameter=85e-3,
        ),
        Transport(
            label="I->II",
            length=0.72,
        ),
        ThreeRollPass(
            label="Stand - II",
            orientation="AntiY",
            roll=Roll(
                groove=FlatGroove(
                    r1=5e-3,
                    usable_width=90e-3,
                    pad_angle=30,
                ),
                nominal_radius=292.3e-3 / 2,
                rotational_frequency=1.913,
            ),
            inscribed_circle_diameter=70e-3,
        )
    ])

    try:
        sequence.solve(in_profile)
    finally:
        print("\nLog:")
        print(caplog.text)

    try:
        from pyroll.report import report
        report = report(sequence)
        f = tmp_path / "report.html"
        f.write_text(report)
        webbrowser.open(f.as_uri())
    except ImportError:
        pass
