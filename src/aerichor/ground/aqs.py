from datetime import datetime
from enum import Enum
import netrc
from pprint import pprint
from time import sleep
from urllib.parse import urljoin

import requests
import pandas as pd

from aerichor.satellite.base import Swath
from aerichor.dataframe import SampleDataFrame


AQS_API_BASE_URL = "https://aqs.epa.gov/data/api/"


# Retrieved using list/parametersByClass endpoint with pc="AQI_POLLUTANTS"
# Note: Returned values probably aren't all the same for each pollutant.
# Example: FRM vs FEM is probably only relevant for PM2.5, right?
class AqiPollutant(Enum):
    CO = 42101  # Carbon monoxide
    SO2 = 42401  # Sulfur dioxide
    NO2 = 42602  # Nitrogen dioxide (NO2)
    O3 = 44201  # Ozone
    PM10 = 81102  # PM10 Total 0-10um STP
    PM25 = 88101  # PM2.5 - Local Conditions
    PM25SM = 88502  # Acceptable PM2.5 AQI & Speciation MASS


class AqsClient:
    # TODO: I could make this a try netrc / fallback to signup or getpass
    def __init__(self, *, login=None, key=None):
        self.login = login
        self.key = key
        self.credentials = {"email": login, "key": key}

    # TODO: Document the usage here. From aqs.py.
    @staticmethod
    def signup(email):
        url = urljoin(AQS_API_BASE_URL, "signup")
        return requests.get(url, params={"email": email})

    @classmethod
    def from_netrc(cls):
        auth = netrc.netrc()
        login, key, _ = auth.authenticators("aqs.epa.gov")
        return cls(login=login, key=key)

    def get(self, endpoint, **kwargs):
        params = self.credentials.copy()
        params.update(kwargs)
        url = urljoin(AQS_API_BASE_URL, endpoint)
        response = requests.get(url, params=params)
        if response.ok:
            sleep(5)
        return response

    def get_pollutant_in_swath(self, pollutant: AqiPollutant, swath: Swath):
        x0, x1, y0, y1 = swath.bbox.to_extent()
        params = dict(
            param=pollutant.value,
            bdate=swath.start.strftime("%Y%m%d"),
            edate=swath.end.strftime("%Y%m%d"),
            minlon=x0,
            maxlon=x1,
            minlat=y0,
            maxlat=y1,
        )
        samples = self.get("sampleData/byBox", **params).json()["Data"]

        # TODO: There's a better way to unpack this because n_obs > n_var
        data = {
            "site_id": [sample["site_number"] for sample in samples],
            "longitude": [sample["longitude"] for sample in samples],
            "latitude": [sample["latitude"] for sample in samples],
            "time": [self._parse_datetime(sample) for sample in samples],
            "measurement": [sample["sample_measurement"] for sample in samples],
        }
        df = SampleDataFrame(data)
        df.units = samples[0]["units_of_measure"]
        df.label = samples[0]["parameter"]
        return df

    @staticmethod
    def _parse_datetime(sample):
        date_string = "".join([sample["date_gmt"], "T", sample["time_gmt"], ":00.00"])
        return datetime.fromisoformat(date_string)
