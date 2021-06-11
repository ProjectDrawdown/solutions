from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest
from mock import patch, MagicMock

import dashboard.charts


def test_make_pie_chart():
    data = pd.DataFrame({"type": ["A", "B", "C"], "count": [1, 2, 3]})
    result = dashboard.charts.make_pie_chart(data, "type", "count", "Title", as_html=False)
    assert result.title.text == "Title"
    data_source = result.renderers[0].data_source
    assert data_source.data["type"].tolist() == ["A", "B", "C"]
    assert data_source.data["count"].tolist() == [1, 2, 3]

    result = dashboard.charts.make_pie_chart(data, "type", "count", "Title", as_html=True)
    assert '<script type="text/javascript">' in result["script"]
    assert "data-root-id" in result["body"]


def test_make_hist_chart():
    data = pd.DataFrame({"scenario": [12, 12, 12, 2, 1, 0]})
    result = dashboard.charts.make_hist_chart(
        data.scenario, "Title", "scenario", "solution", bins=3, as_html=False
    )
    assert result.title.text == "Title"
    data_source = result.renderers[0].data_source
    assert data_source.data["top"].tolist() == [3, 0, 3]
    assert data_source.data["index"].tolist() == [0, 1, 2]

    result = dashboard.charts.make_hist_chart(
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
    result = dashboard.charts.make_comparison_chart(data["A"], "A", "index", "Title", as_html=False)
    assert result.title.text == "Title"
    data_source = result.renderers[0].data_source
    assert data_source.data["index"].tolist() == [
        "afforestation",
        "bamboo",
        "conservationagriculture",
    ]
    assert "A" in data_source.data.keys()

    result = dashboard.charts.make_comparison_chart(data["A"], "A", "index", "Title", as_html=True)

    assert '<script type="text/javascript">' in result["script"]
    assert "data-root-id" in result["body"]
