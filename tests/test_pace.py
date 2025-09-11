import pytest
import shapely

from aerichor.satellite.pace import SpexOne


@pytest.fixture(scope="module")
def spex():
    spex = SpexOne.from_netcdf(
        "tests/data/PACE_SPEXONE.20240324T174414.L2.RTAP_LD.V3_0.nc"
    )
    return spex


def test_base_repr_html_exists(spex):
    assert spex._repr_html_()

# TODO: This test needs to be rewritten.
#def test_base_item_methods(spex):
#    key = "new"
#    value = "test"
#    spex[key] = value
#    assert spex[key] == value
#    del spex[key]
#    with pytest.raises(KeyError):
#        spex[key]


def test_base_swath_contains(spex):
    p = [-78.67, 35.75]
    point = shapely.Point(p)
    assert spex.contains(point)

def test_base_swath_lat_no_min():
    pass