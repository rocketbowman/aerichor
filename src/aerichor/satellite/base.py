from abc import abstractclassmethod

import cartopy.crs as ccrs
from shapely import Polygon
import matplotlib.pyplot as plt

from aerichor.utils import BoundingBox


class Swath:
    def __init__(self, lats, lons, elevation):
        """Swaths define the geometric properties of the satellite pass."""
        self.lats = lats
        self.lons = lons
        self.elevation = elevation

        # ASSUME: Latitude and longitude are ordered from first to last
        first_left = float(lons[0, 0]), float(lats[0, 0])
        first_right = float(lons[0, -1]), float(lats[0, -1])
        last_left = float(lons[-1, 0]), float(lats[-1, 0])
        last_right = float(lons[-1, -1]), float(lats[-1, -1])
        coordinate_seq = [last_left, last_right, first_right, first_left, first_left]

        self.shape = Polygon(coordinate_seq)
        self.bbox = BoundingBox.from_shape(self.shape)
        self.projection = self._get_projection()

    def _get_projection(self):
        lon_mid = float(self.lons.min() + self.lons.max()) / 2
        lat_mid = float(self.lats.min() + self.lats.max()) / 2

        return ccrs.NearsidePerspective(
            central_latitude=lat_mid,
            central_longitude=lon_mid,
            satellite_height=self.elevation,
        )

    def contains(self, other):
        return self.shape.contains(other)

    def show(self):
        # TODO: I'll actually need to process the lats and lons
        # ALT: I can probably just plot swath.shape with the right transform
        x, y = self.shape.exterior.xy
        x.reverse()
        y.reverse()
        ax = plt.subplot(111, projection=self.projection)
        ax.stock_img()
        ax.coastlines()
        ax.plot(x, y, marker="o", transform=ccrs.Geodetic())
        ax.fill(x, y, "coral", transform=ccrs.Geodetic(), alpha=0.4)
        ax.gridlines()
        plt.show()


class Satellite:
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
        self.data = data
        self.elevation = elevation
        self.lats = lats
        self.lons = lons
        self.origin = origin
        self.start = start
        self.end = end
        self.swath = Swath(lats, lons, elevation)

        if hasattr(self.data, "_repr_html_"):
            self._repr_html_ = self.data._repr_html_

    @abstractclassmethod
    def from_netcdf(cls):
        """Reads a netcdf file and returns subclass of Satellite."""
        msg = f"The from_netcdf() method has not been implemented for {cls}."
        raise NotImplementedError(msg)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, item):
        del self.data[item]
