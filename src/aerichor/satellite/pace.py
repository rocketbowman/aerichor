from datetime import datetime, timedelta
from pathlib import Path

import xarray as xr

from aerichor.satellite.base import Swath


PACE_ELEVATION = 6_765_000  # meters


class SPEXOne(Swath):
    def __init__(self, **kwargs):
        super().__init__(elevation=PACE_ELEVATION, **kwargs)

    @classmethod
    def from_netcdf(cls, file):
        """Create Swath from PACE_SPEXONE.*.L2.RTAP_LD.V3_0.nc file."""
        origin = file
        data = xr.open_datatree(file, decode_timedelta=False)
        lats = data["geolocation_data"]["latitude"]
        lons = data["geolocation_data"]["longitude"]
        start = SPEXOne._get_start(file)
        end = SPEXOne._get_end(start)
        return cls(data=data, origin=origin, lats=lats, lons=lons, start=start, end=end)

    # ASSUME: The file is not renamed between being downloaded and read.
    @staticmethod
    def _get_start(file):
        """Get the start time from the file name."""
        name = Path(file).name
        iso_date = name.split(".")[1]
        return datetime.fromisoformat(iso_date)

    # ASSUME: Every swath is exactly 5 minutes long.
    @staticmethod
    def _get_end(start):
        """Add 5 minutes to start time to get end time."""
        return start + timedelta(minutes=5)
