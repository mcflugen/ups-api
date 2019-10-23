|Build Status| |License: MIT| |Code style: black| |Launch Binder| |PyPI|

=======
UPS-API
=======

Python library and command line tools to query the UPS API

*******
Install
*******

To install the *UPS-API* command-line tools and package,

.. code:: bash

   $ pip install ups-api

If installing from source, run the following in the root folder of the repository,

.. code:: bash

   $ pip install -e .

*****
Usage
*****

Command line
============

To validate just a single address,

.. code:: bash

   $ ups xav "1600 Pennsylvania Avenue NW, Washington, DC, 20500"
   1600 PENNSYLVANIA AVE NW,WASHINGTON,DC,20500

Sometimes there will be more than one candidate,

.. code:: bash

   $ ups xav "1600 Pennsylvania Avenue NW, Washington, DC, 20501"
   1600 PENNSYLVANIA AVE NW,WASHINGTON,DC,20500
   1600 PENNSYLVANIA AVE NW,WASHINGTON,DC,20502

The *ups* command can also be run in batch mode where it reads addresses from
a *CSV* file (the csv file is of the form *street*, *city*, *state*, *zip*),

.. code:: bash

   $ ups xav-batch addresses.csv -o validated_addresses.csv


Python
======

To validate an address in *Python* use the *UpsXav* class,

.. code:: python

    >>> from ups import Address, UpsXav
    >>> address = Address.from_str(
    ...   "1600 Pennsylvania Avenue NW, Washington, DC, 20501"
    ... )
    >>> xav = UpsXav()
    >>> addresses = xav.post(address)
    >>> for address in addresses:
    ...   print(address)

This will print the following::

    1600 PENNSYLVANIA AVE NW,WASHINGTON,DC,20500
    1600 PENNSYLVANIA AVE NW,WASHINGTON,DC,20502

***************
The UPS XAV API
***************

A typical request to the UPS Street-level address validator will look
something like the following:

.. code:: python

    >>> data = {
        "UPSSecurity": {
            "UsernameToken": {"Username": YOUR_USERNAME, "Password": YOUR_PASSWORD},
            "ServiceAccessToken": {"AccessLicenseNumber": YOUR_LICENSE},
        },
        "XAVRequest": {
            "Request": {
                "RequestOption": "1",
                "TransactionReference": {"CustomerContext": ""},
            },
            "MaximumListSize": "10",
            "AddressKeyFormat": {
                "ConsigneeName": "",
                "BuildingName": "",
                "AddressLine": "1600 Pennsylvania Avenue NW",
                "PoliticalDivision2": "Washington",
                "PoliticalDivision1": "DC",
                "PostcodePrimaryLow": "20500",
                "CountryCode": "US",
            },
        },
    }

And then to validate,

.. code:: python

    >>> url = "https://onlinetools.ups.com/rest/XAV"
    >>> response = requests.post(url, json=data)

This will generate the following response,

.. code:: python

    {
        "XAVResponse": {
            "Response": {
                "ResponseStatus": {"Code": "1", "Description": "Success"},
                "TransactionReference": {"CustomerContext": ""},
            },
            "ValidAddressIndicator": "",
            "Candidate": {
                "AddressKeyFormat": {
                    "AddressLine": "1600 PENNSYLVANIA AVE NW",
                    "PoliticalDivision2": "WASHINGTON",
                    "PoliticalDivision1": "DC",
                    "PostcodePrimaryLow": "20500",
                    "PostcodeExtendedLow": "0005",
                    "Region": "WASHINGTON DC 20500-0005",
                    "CountryCode": "US",
                }
            },
        }
    }

All the stuff you need is in the *Candidate* section. If there are multiple
candidates, the value of *Candidate* will be a list of *AddressKeyFormat*
objects rather than a single object. If there are no candidates, the
section will be empty.

.. |Build Status| image:: https://travis-ci.org/mcflugen/ups-api.svg?branch=master
   :target: https://travis-ci.org/mcflugen/ups-api
.. |License: MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
.. |Launch Binder| image:: https://static.mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/mcflugen/ups-api.git/master?filepath=notebooks%2Fups-xav.ipynb
.. |PyPI| image:: https://badge.fury.io/py/ups-api.svg
    :target: https://badge.fury.io/py/ups-api
