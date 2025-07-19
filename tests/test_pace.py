import pytest
import shapely

from aerichor.satellite.pace import SPEXOne


@pytest.fixture(scope="module")
def swath():
    swath = SPEXOne.from_netcdf("tests/data/PACE_SPEXONE.20240324T174414.L2.RTAP_LD.V3_0.nc")
    return swath

def test_base_repr_html_exists(swath):
    assert swath._repr_html_()

def test_base_item_methods(swath):
    key="new"
    value="test"
    swath[key]=value
    assert swath[key] == value
    del swath[key]
    with pytest.raises(KeyError):
        swath[key]

def test_base_swath_contains(swath):
    point=shapely.Point(-78.67, 35.75)
    assert swath.swath.contains(point)