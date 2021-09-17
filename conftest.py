
import os
import subprocess
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Copied from numpy code by way of https://stackoverflow.com/a/63775093/1539989 and altered.
# Add git version / branch info to header

def pytest_report_header(config=None):
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v
        out = subprocess.Popen(cmd, stdout = subprocess.PIPE, env=env).communicate()[0]
        return out.strip().decode('ascii')

    try:
        git_branch = _minimal_ext_cmd(['git','branch','--show-current'])
    except OSError:
        git_branch = "unknown"
    
    try:
        git_info= _minimal_ext_cmd(['git','describe','--tags'])
    except OSError:
        git_info = ""
    
    return "Git: " + git_info + " (" + git_branch + ")"