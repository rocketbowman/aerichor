"""
This module defines the basic interface for satellite-retrieved data.

Classes
-------
Swath:
    Defines the geometric properties of satellite-retrived data.
Satellite:
    Define the interface for subclasses.
"""
from abc import abstractclassmethod

import cartopy.crs as ccrs
from shapely import Polygon
import matplotlib.pyplot as plt

from aerichor.utils import BoundingBox
from aerichor.dataframe import SampleDataFrame


class Swath:
    """Contains the geometric properties of satellite-retrieved data."""
    @property
    def lats(self):
        return self._lats

    @lats.setter
    def lats(self, lats):
        if not hasattr(lats, "min") or not hasattr(lats, "max"):
            raise TypeError(f"{type(lats)} does not have a min() or max() method.")
        self._lats = lats

    @property
    def lons(self):
        return self._lons

    @lons.setter
    def lons(self, lons):
        if not hasattr(lons, "min") or not hasattr(lons, "max"):
            raise TypeError(f"{type(lons)} does not have a min() or max() method.")
        self._lons = lons

    @property
    def elevation(self):
        return self._elevation

    @elevation.setter
    def elevation(self, elevation):
        self._elevation = elevation

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        self._end = end

    # TODO: This assumes lats and lons are 2D - not always true
    # BETTER: coords = [Point(*coord) for coord in zip(latitude, longitude)]
    # The problem is that SpexOne (for example) collects points by scanning
    # left-to-right, top-to-bottom. You get a zig-zag shape when you reach 
    # the end of one line and scan back to the beginning of the next line.
    @property
    def shape(self):
        """Returns the shape of the swath as a shapely.Polygon."""
        if not hasattr(self, "._shape") or not self._shape:
            # ASSUME: Latitude and longitude are ordered from first to last
            first_left = float(self.lons[0, 0]), float(self.lats[0, 0])
            first_right = float(self.lons[0, -1]), float(self.lats[0, -1])
            last_left = float(self.lons[-1, 0]), float(self.lats[-1, 0])
            last_right = float(self.lons[-1, -1]), float(self.lats[-1, -1])
            coordinate_seq = [
                last_left,
                last_right,
                first_right,
                first_left,
                first_left,
            ]
            self._shape = Polygon(coordinate_seq)
        return self._shape

    @property
    def bbox(self):
        """Returns the grid-aligned bounding box of the Swath."""
        if not hasattr(self, "._bbox") or not self._bbox:
            self._bbox = BoundingBox.from_shape(self.shape)
        return self._bbox

    def _get_projection(self):
        lon_mid = float(self.lons.min() + self.lons.max()) / 2
        lat_mid = float(self.lats.min() + self.lats.max()) / 2

        return ccrs.NearsidePerspective(
            central_latitude=lat_mid,
            central_longitude=lon_mid,
            satellite_height=self.elevation,
        )

    def contains(self, other):
        """Returns True if the other shape is within the Swath.
        
        Parameters
        ----------
        other: shapely.Shape
            Specifies the shape to query.
            
        Returns
        -------
        bool:
            Returns True if the other shape is within the Swath."""
        return self.shape.contains(other)

    def show_swath(self):
        """Plots the area covered by the swath over the globe."""
        x, y = self.shape.exterior.xy
        x.reverse()
        y.reverse()
        ax = plt.subplot(111, projection=self._get_projection())
        ax.stock_img()
        ax.coastlines()
        ax.plot(x, y, marker="o", transform=ccrs.Geodetic())
        ax.fill(x, y, "coral", transform=ccrs.Geodetic(), alpha=0.4)
        ax.gridlines()
        plt.show()


class Satellite(Swath):
    def __init__(
        self,
        *,
        data=None,
        elevation=None,
        lats=None,
        lons=None,
        origin=None,
        start=None,
        end=None,
    ):
        # Swath attributes
        self.lats = lats
        self.lons = lons
        self.elevation = elevation
        self.start = start
        self.end = end

        # Data Attributes
        self.data = data
        self.origin = origin

        if hasattr(self.data, "_repr_html_"):
            self._repr_html_ = self.data._repr_html_

    @abstractclassmethod
    def from_netcdf(cls):
        """Reads a netcdf file and returns subclass of Satellite."""
        msg = f"The from_netcdf() method has not been implemented for {cls}."
        raise NotImplementedError(msg)

    def __getitem__(self, item):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, item):
        del self.data[item]
