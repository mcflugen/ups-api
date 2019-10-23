import getpass
import io
import logging
import os
from collections import OrderedDict

import pandas as pd
import requests


class AddressParseError(Exception):
    def __init__(self, address):
        self._address = address

    def __str__(self):
        return "unable to parse ({0})".format(self._address)


class Address:
    def __init__(self, address=None, city=None, state=None, zip=None):
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip

    @property
    def address(self):
        return self._street_address

    @address.setter
    def address(self, val):
        if isinstance(val, (tuple, list)):
            val = " ".join(val)
        self._street_address = val.strip()

    @property
    def city(self):
        return self._city

    @city.setter
    def city(self, new_city):
        self._city = new_city.strip()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state.strip()

    @property
    def zip(self):
        return self._zip

    @zip.setter
    def zip(self, new_zip):
        self._zip = str(int(new_zip)).strip()

    def items(self):
        return (
            ("address", self.address),
            ("city", self.city),
            ("state", self.state),
            ("zip", self.zip),
        )

    def as_dict(self):
        return dict(self.items())

    def jsonify(self):
        return {
            "ConsigneeName": "",
            "BuildingName": "",
            "AddressLine": self.address,
            "PoliticalDivision2": self.city,
            "PoliticalDivision1": self.state,
            "PostcodePrimaryLow": self.zip,
            "CountryCode": "US",
        }

    @classmethod
    def from_str(cls, address, sep=","):
        address = pd.read_csv(
            io.StringIO(address), sep=sep, names=("address", "city", "state", "zip")
        )
        return cls(**address.iloc[0])

    def __str__(self):
        return (
            pd.DataFrame([OrderedDict(self.items())])
            .to_csv(header=False, index=False)
            .strip()
        )

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()


class UpsCredentials:
    def __init__(self, username=None, password=None, license=None):
        self._password = (
            password
            or os.environ.get("UPS_PASSWORD", None)
            or getpass.getpass(prompt="Password: ")
        )
        self._username = (
            username
            or os.environ.get("UPS_USERNAME", None)
            or getpass.getpass(prompt="Username: ")
        )
        self._license = (
            license
            or os.environ.get("UPS_LICENSE", None)
            or getpass.getpass(prompt="License: ")
        )

    def jsonify(self):
        return {
            "UsernameToken": {"Username": self._username, "Password": self._password},
            "ServiceAccessToken": {"AccessLicenseNumber": self._license},
        }


class UpsXav:
    URL = "https://onlinetools.ups.com/rest/XAV"

    def __init__(self, username=None, password=None, license=None):
        self._credentials = UpsCredentials(
            username=username, password=password, license=license
        )
        self._data = {
            "UPSSecurity": self._credentials.jsonify(),
            "XAVRequest": {
                "Request": {
                    "RequestOption": "1",
                    "TransactionReference": {"CustomerContext": ""},
                },
                "MaximumListSize": "10",
                "AddressKeyFormat": None,
            },
        }

    def post(self, address):
        self._data["XAVRequest"]["AddressKeyFormat"] = address.jsonify()
        response = requests.post(UpsXav.URL, json=self._data)

        data = response.json()
        if "XAVResponse" not in data:
            raise ValueError(response.text)

        return UpsXav.objectify_collection(data)

    @staticmethod
    def objectify_collection(data):
        try:
            candidates = data["XAVResponse"]["Candidate"]
        except KeyError:
            candidates = []

        if isinstance(candidates, dict):
            candidates = [candidates]

        return [UpsXav.objectify_address(c["AddressKeyFormat"]) for c in candidates]

    @staticmethod
    def objectify_address(data):
        return Address(
            address=data["AddressLine"],
            city=data["PoliticalDivision2"],
            state=data["PoliticalDivision1"],
            zip=data["PostcodePrimaryLow"],
        )


class UpsXavBatch(UpsXav):
    def __init__(self, *args, **kwds):
        super(UpsXavBatch, self).__init__(*args, **kwds)
        self._success = 0
        self._warning = 0
        self._error = 0

    def post_all(self, addresses):
        return self.iter(addresses)

    def iter(self, addresses):
        addresses = pd.read_csv(
            addresses, sep=",", names=("address", "city", "state", "zip")
        )

        class _post_iter:
            def __init__(self, validator):
                self._validator = validator

            def __iter__(self):
                for index, address in addresses.iterrows():
                    try:
                        candidates = self._validator.post(Address(**address))
                    except AddressParseError as error:
                        candidates = []
                        self._validator.on_failure(address, error)
                    else:
                        self._validator.on_success(address, candidates)
                    yield candidates

            def __len__(self):
                return len(addresses)

        return _post_iter(self)

    def on_success(self, address, candidates):
        self._success += 1

    def on_failure(self, address, error):
        self._error += 1

    @property
    def success(self):
        return self._success

    @property
    def warning(self):
        return self._warning

    @property
    def error(self):
        return self._error


class UpsXavBatchAndLogger(UpsXavBatch):
    def __init__(self, username=None, password=None, license=None):
        super(UpsXavBatchAndLogger, self).__init__(
            username=username, password=password, license=license
        )

        handler = logging.FileHandler("xav.log")  # , mode="w")
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("%(asctime)s:UPS-XAV:%(levelname)s:%(message)s")
        )
        self._logger = logging.getLogger("ups-xav")
        self._logger.addHandler(handler)

    def on_success(self, address, candidates):
        super(UpsXavBatchAndLogger, self).on_success(address, candidates)
        if len(candidates) == 0:
            self._logger.warning(
                "no candidates found: {0}".format(str(Address(**address)))
            )
            self._warning += 1

    def on_failure(self, address, error):
        super(UpsXavBatchAndLogger, self).on_failure(address, error)
        self._logger.error("unable to parse address: {0}".format(str(error)))
