
import sys
import pathlib

root_path = pathlib.Path(__file__).parents[1].resolve().as_posix()
sys.path.append(root_path)

from dashboard.generator import generate_html

DASHBOARD_FILE = "index.html"

html = generate_html()
with open(DASHBOARD_FILE, "w") as f:
    f.write(html)
