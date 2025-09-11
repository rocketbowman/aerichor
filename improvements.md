# Improvements

This is a list of things that I would prioritize to improve.

## Terminology note

An `xarray.DataArray` is basically the same as a `Pandas.DataFrame`. 
I don't guarantee that I don't use those interchangeably. Sometimes I use the term data frame for any frame-like thing. 

An `xarray.DataTree` is a hierarchical arrangement of `DataArrays`. There
is no Pandas equivalent that I know of.

## SampleDataFrame -> GeoPandas DataFrame

The `SampleDataFrame` resulted from frustrations of working with the
`xarray.DataTree` from `SpexOne`. There's a lot of good with `xarray.DataTrees`
but these particular ones use `number_of_lines`, and `pixels_per_line` as
coordinates. That's great from the satellite's perspective, but in modeling, I
want to see how the measurements vary with latitude and longitude. The
`SampleDataFrame` is intended to hold that data at the ready. It was also
a good place to add with additional useful features, like `get_spatial_value`.

By the time I finished writing the `get_spatial_value`, I realized that I
probably just reinvented spatial joins very crudely. But by this point, it 
worked and doing it better would involve breaking what I just finished.

Given more time, I'd look into using a `GeoDataFrame` as the main data
structure. This doc highlights what seems like a promising way to replace the 
`get_spatial_value` method with a more standard and tested approach.

## SampleDataFrame/GeoDataFrame Design or Validation

I think ideally, users wouldn't have to create this construct themselves. 
Instead, we would hand it to them as the result of, for example,
`SpexOne.from_netcdf()` or `AqsClient.get_pollutants_from_swath()`. Keeping with
current design goals it's nice to say "you can do with this object anything that
you would do with a normal Pandas (or GeoPandas) DataFrame plus a few more
things."

Some of the methods rely on specific columns. Like having "longitude" or
"latitude". If we ever expect users to create one of these objects and we still
rely on the data being formed in a certain way, we need to catch invalid data
early.

## Profiling Satellite Data

For `Pandas.DataFrames`, you can run `df.describe()` to summarize each of the
columns. I think that it would be similarly nice to do the same thing for
instances of `Satellite`. What's preventing that now is the layout of the
`xarray.DataArray`. But if you can standardize the `Satellite` layout so that
it's essentially a `DataFrame`, you should be able to do the same.

Another challenge is that the xarray has a 2-D layout of latitude and longitude.
Each is indexed by `number_of_lines` and `pixels_per_line`. I had thought about
flattening them and creating a grid where latitude and longitude were the axes,
but the data would have been sparse. I'm starting to think that it would be
better to store latitude and longitude together as a single column of
`Point(lon,lat)`. (Idea stolen from the GeoPandas example, which I'm realizing more and more is pretty brilliant.)

With standardized data consisting of "points", "val1", "val2", _etc._, it would
be easy to convert to a `DataFrame` on-the-fly to describe it.

## More Data Integrations

* `SpexOne` is a model for other Earthdata integrations.
* `AqsClient` is a decent model for other API query-based data. I think Aeronet
  has a similar mechanism.

## Miscellaneous

* `within_timeframe(start, end)` would be a nice method to add to the custom
  DataFrame. I didn't see anything like that in GeoPandas, but it would be worth checking first. 
* `align_temporally` - Currently keeps only the observations nearest in time to
  the specified time. You could conceive of other strategies than "nearest." Maybe you make one method and add a "strategy" parameter. Maybe you create a different method per strategy.
* `get_spatial_value` - Currently aggregates all "near" points by taking the
  mean of those points. Like `align_temporally`, it's easy to conceive of other
  strategies. Similarly, there are other definitions for "near".
* `Satellite.__getitem__` assumes that you are retrieving a variable that is 
  indexed by latitude and longitude. But nothing in the `Satellite` constructor
  guarantees that condition for each item. You might be able to hack that check
  into `__getitem__`. I kinda like the `__getitem__` functionality, but it's 
  unexpected. Maybe it would be better in a uniquely named method.
* Sketch out an API for data-fetching functionality for `SpexOne`/`Satellite`. 
  Maybe define a mixin for retrieving data from Earthdata.
