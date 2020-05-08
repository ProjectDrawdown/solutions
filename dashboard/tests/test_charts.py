from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
from mock import patch, MagicMock

from dashboard.charts import make_hist_chart, make_pie_chart, make_comparison_chart


def test_make_pie_chart():
    data = pd.DataFrame({"type": ["A", "B", "C"], "count": [1, 2, 3]})
    result = make_pie_chart(data, "type", "count", "Title", as_html=False)
    assert result.title.text == "Title"
    data_source = result.renderers[0].data_source
    assert data_source.properties_with_values()["data"]["type"] == ["A", "B", "C"]
    assert data_source.properties_with_values()["data"]["count"] == [1, 2, 3]

    result = make_pie_chart(data, "type", "count", "Title", as_html=True)
    assert '<script type="text/javascript">' in result["script"]
    assert "data-root-id" in result["body"]


def test_make_hist_chart():
    data = pd.DataFrame({"scenario": [12, 12, 12, 2, 1, 0]})
    result = make_hist_chart(
        data.scenario, "Title", "scenario", "solution", bins=3, as_html=False
    )
    assert result.title.text == "Title"
    data_source = result.renderers[0].data_source
    assert data_source.properties_with_values()["data"]["top"] == [3, 0, 3]
    assert data_source.properties_with_values()["data"]["index"] == [0, 1, 2]

    result = make_hist_chart(
        data.scenario, "Title", "scenario", "solution", bins=3, as_html=True
    )
    assert '<script type="text/javascript">' in result["script"]
    assert "data-root-id" in result["body"]


def test_make_comparison_chart():
    data = pd.DataFrame(
        {
            "A": {
                "afforestation": 100.0,
                "bamboo": 67.62772779062492,
                "conservationagriculture": 51.012337313714646,
            }
        }
    )
    result = make_comparison_chart(data["A"], "A", "index", "Title", as_html=False)
    assert result.title.text == "Title"
    data_source = result.renderers[0].data_source
    assert data_source.properties_with_values()["data"]["index"] == [
        "afforestation",
        "bamboo",
        "conservationagriculture",
    ]
    assert "A" in data_source.properties_with_values()["data"].keys()

    result = make_comparison_chart(data["A"], "A", "index", "Title", as_html=True)

    assert '<script type="text/javascript">' in result["script"]
    assert "data-root-id" in result["body"]
