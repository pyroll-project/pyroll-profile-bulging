import logging
import webbrowser
from pathlib import Path
from pyroll.core import Profile, Roll, ThreeRollPass, Transport, CircularOvalGroove, SquareGroove, PassSequence


def test_solve_3rp_round_oval_oval(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.profile_bulging

    in_profile = Profile.round(
        diameter=71e-3,
        temperature=1000 + 273.15,
        strain=0,
        material=["S304", "steel"],
        flow_stress=100e6,
        length=1,
        density=7.5e3,
        specific_heat_capacity=690,
        thermal_conductivity=23
    )

    sequence = PassSequence([
        ThreeRollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    usable_width=67.12e-3,
                    r1=0.1e-3,
                    r2=129e-3 / 2,
                    pad_angle=30
                ),
                nominal_radius=195e-3 / 2,
                rotational_frequency=130 * 1 / 60
            ),
            inscribed_circle_diameter=59.9e-3,
        ),
        Transport(
            label="I => II",
            duration=1
        ),
        ThreeRollPass(
            label="Oval II",
            roll=Roll(
                groove=CircularOvalGroove(
                    usable_width=62.37e-3,
                    r1=0.1e-3,
                    r2=129e-3 / 2,
                    pad_angle=30
                ),
                nominal_radius=197e-3 / 2,
                rotational_frequency=100 * 1 / 60
            ),
            inscribed_circle_diameter=54.4e-3,
        ),
        Transport(
            label="II => III",
            duration=1
        ),
        ThreeRollPass(
            label="Oval III",
            roll=Roll(
                groove=CircularOvalGroove(
                    usable_width=56.25e-3,
                    r1=0.1e-3,
                    r2=129e-3 / 2,
                    pad_angle=30
                ),
                nominal_radius=201e-3 / 2,
                rotational_frequency=100 * 1 / 60
            ),
            inscribed_circle_diameter=47.7e-3,
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
