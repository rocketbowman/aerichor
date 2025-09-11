"""
This module facillitates interation with the Environmental Protection Agency's
(EPA) Air Quality Service (AQS) Application Programming Interface (API).

The API is documented here:
https://aqs.epa.gov/aqsweb/documents/data_api.html

Classes
-------
AqiPollutant:
    Maps human-readable names to the key used by the AQS API service
AqsClient:
    Manages data requests the the AQS API service.
"""
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


class AqiPollutant(Enum):
    """Maps human-readable names to the key used by the AQS API service.

    You can retrieve a thorough list of pollutants by submitting a request to
    the list/parametersByClass endpoint with the parameter pc="AQI_POLLUTANTS".
    It is possible that different pollutants have different fields in the returned
    value.
    """
    CO = 42101   # Carbon monoxide
    SO2 = 42401  # Sulfur dioxide
    NO2 = 42602  # Nitrogen dioxide (NO2)
    O3 = 44201   # Ozone
    PM10 = 81102  # PM10 Total 0-10um STP
    PM25 = 88101  # PM2.5 - Local Conditions
    PM25SM = 88502  # Acceptable PM2.5 AQI & Speciation MASS


class AqsClient:
    """Manages data requests to the EPA's AQS service. 

    The AQS service requires you to provide your credentials each time you 
    make a request to the service. The AqsClient class manages those 
    credentials for you and offers a Python interface to common requests.
    
    Parameters
    ----------
    login: email
        Specifies the login ID of your credentials. Login is determined by 
        the email address that you registered when you signed up for your
        account.
    key: str
        Specifies the string that is used to validate your credentials. This 
        value is provided to you when you validate your email address.

    Attributes
    ----------
    login: email
        Stores the login value.
    key: str
        Stores the key value.
    credentials: 
        Stores a dictionary that contains the login and key in a format that
        is easily included in your AQS requests.

    Returns
    -------
    self
    """
    # TODO: I could make this a try netrc / fallback to signup or getpass
    def __init__(self, *, login=None, key=None):
        self.login = login
        self.key = key
        self.credentials = {"email": login, "key": key}

    @staticmethod
    def signup(email):
        """Registers an email address with the AQS API service.

        When the AQS service receives this request, it sends an email to the
        provided address. You must validate that email to retrieve your
        key to complete your credentials.

        Parameters
        ----------
        email: email
            Specifies the email address that you would like to register.

        Returns
        -------
        requests.Response
        """
        url = urljoin(AQS_API_BASE_URL, "signup")
        return requests.get(url, params={"email": email})

    @classmethod
    def from_netrc(cls):
        """Creates an AqsClient from credentials in your netrc file.

        A netrc file is a private per-user file that contains login information
        for various services. An entry for the AQS service looks like the
        following:

        machine aqs.epa.gov
        login <email-address>
        account <key>

        Parameters
        ----------
        None
        
        Returns
        -------
        self 
        """
        auth = netrc.netrc()
        login, key, _ = auth.authenticators("aqs.epa.gov")
        return cls(login=login, key=key)

    def get(self, endpoint, **kwargs):
        """Issues a general request to the AQS service.

        This method performs a general HTTP request. You must specify an
        endpoint and all non-credential parameters. You must unpack the result
        from the response.

        Endpoing and parameter descriptions are found here:
        https://aqs.epa.gov/aqsweb/documents/data_api.html

        Parameters
        ----------
        endpoint: str
            Specifies the endpoint of the AQS service to target. 
        **kwargs: key-value pairs
            Specifies the parameters to provide to the AQS service. A detailed
            list of parameters is found here:

        Returns
        -------
        request.Response 
        """
        params = self.credentials.copy()
        params.update(kwargs)
        url = urljoin(AQS_API_BASE_URL, endpoint)
        response = requests.get(url, params=params)
        if response.ok:
            # Built-in delay so we don't accidentally spam server:
            # https://aqs.epa.gov/aqsweb/documents/data_api.html#terms
            sleep(5)
        return response

    def get_pollutant_in_swath(self, pollutant: AqiPollutant, swath: Swath):
        """Retrieves measurements of a pollutant within a Swath's bounding box.

        This method retrieves all measurements of a pollutant from all sensors
        within the Swath's bounding box on the date of the Swath then unpacks it
        into a SampleDataFrame. 
        
        Because a bounding box is grid-aligned, many sensors might fall outside
        of the Swath's path. 
        
        This method contains a built-in 5s delay so that you do not accidentally
        exceed the API rate requests. Because this method is capped at a day's
        worth of sensor data, you generally do not need to worry about exceeding
        the limit for data volume per request.

        Parameters
        ----------
        pollutant: AqiPollutant.{CO, SO2, NO2, O3, PM10, PM25, PM25SM}
            Specifies the pollutant measurements to retrieve.
        swath:
            Specifies the reference Swath, whose bounding box is used in the 
            API request. 

        Returns
        -------
        SampleDataFrame
            Contains latitude, longitude, site_id, time, and the pollutant's
            measurement.
        """
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

        # There's a better way to unpack this because n_obs > n_var.
        # Might be worth fixing, but I suspect the built-in 5s delay dominates.
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
        """Reads a date string from the AQS service and returns a datetime object."""
        date_string = "".join([sample["date_gmt"], "T", sample["time_gmt"], ":00.00"])
        return datetime.fromisoformat(date_string)
