import pytest
import shapely

from aerichor.utils import BoundingBox


@pytest.fixture
def bbox():
    shape = shapely.Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    return BoundingBox.from_shape(shape)


def test_bbox_to_extent(bbox):
    assert bbox.to_extent() == (0, 10, 0, 10)
    assert bbox.to_extent(buffer=5) == (-5, 15, -5, 15)


def test_bbox_contains_point(bbox):
    assert (1, 5) in bbox
    assert [1, 5] in bbox
    assert shapely.Point(1, 5) in bbox


def test_bbox_not_contains_point(bbox):
    assert (0, 5) not in bbox


def test_bbox_contains_line(bbox):
    assert shapely.LineString([(1, 1), (2, 2)]) in bbox
