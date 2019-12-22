"""Tests for excel_fair_results.py"""

import pathlib
import subprocess
import pytest

this_dir = pathlib.Path(__file__).parents[0]


@pytest.mark.slow
def test_invoke_script():
    script = str(this_dir.joinpath('test_excel_fair_results.sh'))
    topdir = str(this_dir.parents[1])
    rc = subprocess.run([script, topdir], capture_output=True, timeout=120)
    assert rc.returncode == 0, rc.stdout
