from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytest

from aerichor import SampleDataFrame


@pytest.fixture
def df():
    data ={
        'latitude': [0, 2, 4, 6, 8],
        'longitude': [-0, -2, -4, -6, -8],
        'measurement': [0, 0.2, 0.4, 0.6, 0.8],
        'id' : [1, 1, 2, 2, 3],
        'time': [datetime(2025, 1, 1, 12, 20),
                 datetime(2025, 1, 1, 13, 20),
                 datetime(2025, 1, 1, 14, 20),
                 datetime(2025, 1, 1, 15, 20),
                 datetime(2025, 1, 1, 16, 20)]
    }
    return SampleDataFrame(data)


def test_align_temporally(df):
    dt=datetime(2025,1,1,14)
    computed = df.align_temporally(dt, groupby="id")
    target = [datetime(2025,1,1,13,20),datetime(2025,1,1,14,20),datetime(2025,1,1,16,20)]
    assert (computed['id'].values == np.array([1, 2, 3])).all()
    assert (computed['time'].values == np.array(target, dtype='datetime64')).all()

def test_get_spatial_value(df):
    data = {
        'value': [0, 2, 4, 6, 8], 
        'latitude': [0, 3, 6, 9, 12], 
        'longitude': [-0,-3,-6,-9,-12]
        }
    other = pd.DataFrame(data)
    computed = df.get_spatial_value(other, 'value', buffer=0.25)
    target = pd.Series([0, 4])
    # only df observations 0 and 3 have matching coordinates in other
    # the other rows are assigned a null value.
    assert (computed[computed.notnull()] == target.values).all()
    assert computed.isnull().sum() == 3

def test_normal_pandas_stuff(df):
    assert isinstance(df['id'], pd.Series)
    assert isinstance(df.iloc[0:2], pd.DataFrame)