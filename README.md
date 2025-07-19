# Overview

This is a Python utility library for analysing geospatial aerosol data.

# About the Name

You know that earthy smell right after it starts raining? That's called
petrichor, which comes from two distinct Greek word roots. The "petr-" part
means stone. Ichor, is the mythical blood of the gods. So "petrichor" is roughly
"the god-blood of the stone."

# API Example

```python
from shapely import Point
import aerichor.satellite.pace as pace
spex=pace.SPEXOne.from_netcdf("tests/data/PACE_SPEXONE.20240324T174414.L2.RTAP_LD.V3_0.nc")
if spex.swath.contains(Point(-78.5,35.6)):
    print("This point was covered by the satellite pass. Hooray!")
```