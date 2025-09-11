"""
This module contains helpful classes that didn't fit in the rest of the package
structure.

Classes
-------
BoundingBox
"""

import shapely


class BoundingBox:
    """Converts between many different representations of a box.

    Parameters
    ----------
    top_left: float
        Specifies the top-left corner of the box.
    top_right: float
        Specifies the top-right corner of the box.
    bottom_left: float
        Specifies the bottom-left corner of the box.
    bottom_right:
        Specifies the bottom-right corner of the box.

    Attributes
    ----------
    box: shapely.LinearRing
        Contains a LinearRing representation of the box.
    points: dict
        A dictionary of shapely.Point representations of the corners.
    """

    def __init__(
        self, *, top_left=None, top_right=None, bottom_left=None, bottom_right=None
    ):
        kwargs = {
            "top_left": top_left,
            "top_right": top_right,
            "bottom_left": bottom_left,
            "bottom_right": bottom_right,
        }

        # Let's use shapely's own constructors to validate points.
        self.points = {k: shapely.Point(v) for k, v in kwargs.items()}
        self.box = shapely.LinearRing(
            [
                self.points["bottom_left"],
                self.points["bottom_right"],
                self.points["top_right"],
                self.points["top_left"],
            ]
        )

    # NOTE: By casting to a Point, we can use point-like objects, like [0,10]
    def __contains__(self, point):
        if not isinstance(point, shapely.Geometry):
            point = shapely.Point(point)
        polygon = shapely.Polygon(self.box)
        return polygon.contains(point)

    @classmethod
    def from_shape(cls, shape):
        """Creates a grid-aligned bounding box from a given shape.

        Parameters
        ----------
        shape: shapely.Shape
            Specifies the shape that you want to create a bounding box for.

        Returns
        -------
        self
        """
        if not hasattr(shape, "bounds"):
            shape = shapely.LinearRing(shape)
        minx, miny, maxx, maxy = shape.bounds
        kwargs = {
            "top_left": (minx, maxy),
            "top_right": (maxx, maxy),
            "bottom_left": (minx, miny),
            "bottom_right": (maxx, miny),
        }
        return cls(**kwargs)

    def to_extent(self, buffer=0):
        """Writes the box as a tuple that can be used in cartopy's extent parameter.
        
        Parameters
        ----------
        buffer: float, optional
            Specifies a buffer. The buffer is added to the left, right, top, 
            and bottom of the bounding box before returning the result.
        
        Returns
        -------
        tuple of form: (x0, x1, y0, y1)
        """
        p = self.points
        x0 = min(p["top_left"].x, p["bottom_left"].x) - buffer
        x1 = max(p["top_right"].x, p["bottom_right"].x) + buffer
        y0 = min(p["bottom_left"].y, p["bottom_right"].y) - buffer
        y1 = max(p["top_left"].y, p["top_right"].y) + buffer
        return (x0, x1, y0, y1)
