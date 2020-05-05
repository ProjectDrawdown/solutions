from os.path import dirname, abspath
import sys

sys.path.append(dirname(dirname(abspath(__file__))))

from model_health.dashboard import generate_html

DASHBOARD_FILE = "index.html"

html = generate_html()
with open(DASHBOARD_FILE, "w") as f:
    f.write(html)
