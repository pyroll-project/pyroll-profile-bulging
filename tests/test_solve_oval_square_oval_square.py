import logging
import webbrowser
from pathlib import Path
from pyroll.core import Profile, Roll, RollPass, Transport, SquareGroove, CircularOvalGroove, PassSequence


def test_solve_oval_square_oval(tmp_path: Path, caplog):
    caplog.set_level(logging.DEBUG, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.profile_bulging

    in_profile = Profile.from_groove(
        groove=SquareGroove(
            usable_width=40.74e-3,
            tip_depth=20.05e-3,
            r1=7e-3,
            r2=5e-3
        ),
        gap=3e-3,
        filling=0.9,
        temperature=1200 + 273.15,
        strain=0,
        material=["C20", "steel"],
        flow_stress=100e6
    )

    sequence = PassSequence(
        [
            RollPass(
                label="Oval I",
                orientation='h',
                roll=Roll(
                    groove=CircularOvalGroove(
                        depth=7.25e-3,
                        r1=6e-3,
                        r2=44.5e-3
                    ),
                    nominal_radius= (324e-3 + 320e-3) / 2 / 2,

                ),
                velocity=1,
                gap=3e-3,
            ),
            Transport(
                duration=1
            ),
            RollPass(
                label="Quadrat II",
                orientation='v',
                roll=Roll(
                    groove=SquareGroove(
                        usable_width=29.64e-3,
                        tip_depth=14.625e-3,
                        r1=6e-3,
                        r2=4e-3
                    ),
                    nominal_radius=(328e-3 + 324e-3) / 2 / 2
                ),
                velocity=1,
                gap=3e-3,
            )
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
