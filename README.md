# Overview

This is a Python utility library for analysing geospatial aerosol data.

## About the Name

You know that earthy smell right after it starts raining? That's called
petrichor, which comes from two distinct Greek word roots. The "petr-" part
means stone. "Ichor", on the other hand, is the mythical blood of the gods. So
"petrichor" is roughly "the god-blood of the stone." Aerichor then, is "the
god-blood of the air." In other words, I just thought it was a cool name that
wasn't claimed yet.

## Aims of this Package

### Abstract Common Workflows

This package aims to abstract the similarities of data workflows that use
remote-sensing data of aerosols. There are many common tasks amongst these data
workflows. For example, one of the most common ones is getting observations of
one dataset that correspond spatially and temporally with observations of
another dataset.

### Promote Common Data Structures

To abstract behavior, you must have some guarantees about the structure of the 
data. But different research groups package their data in different ways. In
this package, we define dataset specific classes that unpack the data into one 
of a few standard formats.

For example, the `SpexOne` class unpacks data into the standard `Satellite`
paradigm. And by using the `AqsClient`, you can retrieve pollutant data in
the `SampleDataFrame` format.

* The `Satellite` format is characterized by it's `Swath`, which is defined by
  * measurements over an area (defined by latitude and longitude)
  * a start time and end time
  * an elevation from which the measurements were made
* The `SampleDataFrame` is a Pandas `DataFrame` with a few additions. It works
  well for pointwise data. It is defined by a latitude, longitude, and
  measurement. Everything you can do with a Pandas `DataFrame` can also be done with a `SampleDataFrame`.

Conceivably, a lidar-specific format would also be useful because it would be 
characterized by a path (rather than area or points) and elevation. 

# Getting Started

## Installation

## Short Example

This example shows how you can use the `aerichor` API to create a dataset of
spatially and temporally collocated AOD and PM2.5 measurements, where the AOD is
retrieved from 21 satellite passes and the PM2.5 is retrieved from AQS ground
sensor data.


``` python
import pandas as pd
from aerichor.satellite.pace import SpexOne

# Load credentials so you can fetch pollutant data
api=AqsClient.from_netrc()

# For each netcdf in the data dir, add a corresponding Satellite object to the
# list
data_dir = "../data/spexone"
files=[Path(data_dir) / file for file in os.listdir(data_dir)]
passes=[SpexOne.from_netcdf(file) for file in files]

# Iterate over every satellite pass, perform steps; append the results
dataframes = []
for swath in passes:
    # Get PM2.5 data from AQS and clean it with normal DataFrame methods
    pm25=api.get_pollutant_in_swath(AqiPollutant.PM25, sat_case)
    pm25.dropna(inplace=True)
    cleaned=pm25[pm25['measurement'] >= 0].dropna()

    # Keep only the PM2.5 data closest to the time of the satellite pass
    aligned=cleaned.align_temporally(swath.start)

    # For each PM2.5 sensor, get average AOD of values within +/- 0.25 lat/lon
    flat=swath['geophysical_data/aot550'].rename(
        columns={'geophysical_data/aot550':'aot'})
    aligned['aot']=aligned.get_spatial_value(flat, 'aot', buffer=0.25)
    final=aligned[aligned['aot'].notnull()]

    # Append result to list of dataframes
    dataframes.append(final)

main = pd.concat(dataframes,ignore_index=True)
```

## Extended Example

For a longer example with more detailed explanation, look at the Jupyter
notebook.