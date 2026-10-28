"""Self-contained Three.js chart; vendored library also works offline."""
import json
from pathlib import Path


def chart_html(rows, unit):
    root = Path(__file__).parent / "assets"
    payload = json.dumps({"rows": rows, "unit": unit}, allow_nan=False).replace("<", "\\u003c")
    return (root.joinpath("nfl_chart.html").read_text(encoding="utf-8")
            .replace("/* THREE_LIBRARY */", root.joinpath("three.min.js").read_text(encoding="utf-8"))
            .replace("/* CHART_DATA */", payload))
