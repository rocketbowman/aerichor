from abc import abstractclassmethod

from shapely import Polygon

from aerichor.utils import BoundingBox


class Swath:

    def __init__(self, *, data=None, origin=None, elevation=None,
                 lats=None, lons=None, start=None, end=None):
        self.data       = data
        self.lons       = lons
        self.lats       = lats
        self.elevation  = elevation
        self.origin     = origin
        self.start      = start
        self.end        = end
        self.swath      = self._get_swath()
        self.bbox       = BoundingBox.from_shape(self.swath)

        if hasattr(self.data,"_repr_html_"):
            self._repr_html_ = self.data._repr_html_
    
    @abstractclassmethod
    def from_netcdf(cls):
        """Reads a netcdf file and returns subclass of Swath."""
        msg = f"The from_netcdf() method has not been implemented for {cls}."
        raise NotImplementedError(msg)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, item):
        del self.data[item]

    # ASSUME: Latitude and longitude are ordered from first to last
    def _get_swath(self):
        """ Returns the swath of the satellite. """
        first_left  = float(self.lons[0,0]),   float(self.lats[0,0])
        first_right = float(self.lons[0,-1]),  float(self.lats[0,-1])
        last_left   = float(self.lons[-1,0]),  float(self.lats[-1,0])
        last_right  = float(self.lons[-1,-1]), float(self.lats[-1,-1])
        coordinate_seq = [last_left, last_right, first_right, first_left, first_left]
        return Polygon(coordinate_seq)