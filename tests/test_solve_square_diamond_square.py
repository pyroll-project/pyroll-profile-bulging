import logging
import webbrowser
from pathlib import Path
from pyroll.core import Profile, Roll, RollPass, Transport, DiamondGroove, SquareGroove, PassSequence


def test_solve_square_diamond_square(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.profile_bulging

    in_profile = Profile.square(
        side=45e-3,
        corner_radius=3e-3,
        temperature=1200 + 273.15,
        strain=0,
        material=["C20", "steel"],
        flow_stress = 100e6
    )

    sequence = PassSequence([
        RollPass(
            label="Raute I",
            roll=Roll(
                groove=DiamondGroove(
                    usable_width=76.55e-3,
                    tip_depth=22.1e-3,
                    r1=12e-3,
                    r2=8e-3
                ),
                nominal_radius=(324e-3 + 320e-3) / 2 / 2

            ),
            velocity=1,
            gap=3e-3,
        ),
        Transport(
            label="I -> II ",
            duration=1
        ),
        RollPass(
            label="Quadrat II",
            roll=Roll(
                groove=SquareGroove(
                    usable_width=52.7e-3,
                    tip_depth=25.95e-3,
                    r1=8e-3,
                    r2=6e-3
                ),
                nominal_radius=(328e-3 + 324e-3) / 2 / 2,

            ),
            velocity=1,
            gap=3e-3,
        ),
        ]
    )

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
