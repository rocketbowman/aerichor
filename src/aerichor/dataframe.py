import pandas as pd


# TODO: It would be nice to validate that all the required columns are present.
# I don't really expect end users to create these in their analysis.
# But validating at initialization would be useful for developers.
# TODO: The _real_ way to handle this would be to use GeoPandas and to leverage
# their spatial joins.
class SampleDataFrame(pd.DataFrame):
    _metadata = ["units", "label"]

    @property
    def _constructor(self):
        return SampleDataFrame

    # TODO: Is there a good place to hook validation? Currently it's called manually.
    # Also, make this "longitude" in self.columns()
    def _validate(self):
        assert list(self.columns()) == ["longitude", "latitude", "measurement"]

    # TODO: in_bbox is good for general purpose but not needed for AQS
    # because it can be done in the API request.
    def within_shape(self, shape):
        """Return a subset of data that has entries within the bounding box."""
        pass

    # TODO: in_timeframe implies the need for AQS queries to pull timeframe.
    def within_timeframe(self, start, end):
        """Return a subset of data that has entries within the timeframe."""
        pass

    # TODO: Add strategy: "nearest", "midpoint", "daily"?
    # 'site_id' might not be appropriate for all data.
    def align_temporally(self, datetime):
        # datetime can be swath.start (a scalar datetime)
        self["delta_t"] = abs(self["time"] - datetime)
        nearest = self.loc[self.groupby("site_id")["delta_t"].idxmin()]
        return nearest

    # TODO: Alternative aggregators to mean?
    # TODO: Alternative way of determining nearness
    def get_spatial_value(self, other, key, buffer=0.25):
        def _compute_by_row(row):
            is_in_lat = abs(row["latitude"] - other["latitude"]) <= buffer
            is_in_lon = abs(row["longitude"] - other["longitude"]) <= buffer
            return other[is_in_lat & is_in_lon][key].mean()

        return self.apply(_compute_by_row, axis=1)
