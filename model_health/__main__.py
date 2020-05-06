
import sys
import pathlib

sys.path.append(pathlib.Path(__file__).parents[1])

from model_health.dashboard import generate_html

DASHBOARD_FILE = "index.html"

html = generate_html()
with open(DASHBOARD_FILE, "w") as f:
    f.write(html)
