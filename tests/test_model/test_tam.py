import pytest
import solution
from model.tam import TAM
import pandas as pd
import numpy as np
from solution import rrs


def test_tam():
    tamconfig = pd.read_csv(
        "tests/test_model/data/tam/tamconfig.csv", index_col="param", dtype="object"
    )
    # sd_mult rows need to be floats
    tamconfig.loc["high_sd_mult"] = tamconfig.loc["high_sd_mult"].astype("float")
    tamconfig.loc["low_sd_mult"] = tamconfig.loc["low_sd_mult"].astype("float")
    regions = [
        "World",
        "OECD90",
        "Eastern Europe",
        "Asia (Sans Japan)",
        "Middle East and Africa",
        "Latin America",
        "China",
        "India",
        "EU",
        "USA",
        "PDS World",
    ]
    expected_fd = {}
    for region in regions:
        expected_fd[region] = pd.read_csv(
            f"tests/test_model/data/tam/forecast_data__{region}.csv", index_col="Year"
        )

    tam = TAM(
        tamconfig=tamconfig,
        tam_ref_data_sources=rrs.energy_tam_2_ref_data_sources,
        tam_pds_data_sources=rrs.energy_tam_2_pds_data_sources,
    )

    fd = tam._forecast_data

    assert list(fd.keys()) == regions
    for region in regions:
        pd.testing.assert_frame_equal(fd[region], expected_fd[region])

    ref_tam_per_region = tam.ref_tam_per_region()
    pds_tam_per_region = tam.pds_tam_per_region()

    expected_ref_tam = pd.read_csv(
        "tests/test_model/data/tam/ref_tam_per_region.csv", index_col="Year"
    )
    expected_pds_tam = pd.read_csv(
        "tests/test_model/data/tam/pds_tam_per_region.csv", index_col="Year"
    )

    pd.testing.assert_frame_equal(ref_tam_per_region, expected_ref_tam)
    pd.testing.assert_frame_equal(pds_tam_per_region, expected_pds_tam)
