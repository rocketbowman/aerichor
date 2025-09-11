import pandas as pd


class SampleDataFrame(pd.DataFrame):
    """Extends Pandas DataFrame with convenience functions."""
    _metadata = ["units", "label"]

    @property
    def _constructor(self):
        return SampleDataFrame

    def align_temporally(self, datetime, groupby=None):
        """Retains only the observations nearest in time to the specified time.

        Parameters
        ----------
        datetime: datetime
            Specifies the datetime that all observations are compared to.
        groupby: str
            Specifies the column in the data frame that observations should be 
            grouped by. In the resulting data frame, there is one observation
            per value in the groupby value.

        Returns
        -------
        SampleDataFrame
            Contains the same data as the original, but with observations 
            filtered by time. 
        """
        if not groupby:
            msg = "You must specify a variable to use to group observations."
            raise Exception(msg)
        # datetime can be swath.start (a scalar datetime)
        self["delta_t"] = abs(self["time"] - datetime)
        nearest = self.loc[self.groupby(groupby)["delta_t"].idxmin()]
        return nearest

    def get_spatial_value(self, other, column, buffer=0.25):
        """Computes the mean value of all latitude and longitude within a buffer. 

        For each row in the current data frame, compute a value based on data 
        from another data frame. The computed value is the mean value, averaged
        over the latitude and longitude that is "near" the point in the current
        row. A point in the other data frame is "near" the current observation
        if it's latitude and longitude is within plus or minus one buffer width
        of the current row.

        Parameters
        ----------
        other: data frame
            Specifies the frame that contains the data value to compute.
        column: str
            Specifies the name of the column in the other frame that contains
            the value that you want to compute.
        buffer: float, optional
            Specifies how big a space you want to average over. Specifically,
            it refers to how many degrees east and west (for longitude) and
            north and south (for latitude) that you want to average over.
        Returns
        ------- 
        pd.Series
            Contains one value per row in the original data frame. 
        """
        def _compute_by_row(row):
            is_in_lat = abs(row["latitude"] - other["latitude"]) <= buffer
            is_in_lon = abs(row["longitude"] - other["longitude"]) <= buffer
            return other[is_in_lat & is_in_lon][column].mean()

        return self.apply(_compute_by_row, axis=1)