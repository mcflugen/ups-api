import os

from ups import UpsCredentials


def test_create():
    credentials = UpsCredentials(
        username="eric.idle", password="monty", license="123456789"
    )
    assert credentials._username == "eric.idle"
    assert credentials._password == "monty"
    assert credentials._license == "123456789"


def test_jsonify():
    as_json = UpsCredentials(
        username="eric.idle", password="monty", license="123456789"
    ).jsonify()
    assert as_json["UsernameToken"]["Username"] == "eric.idle"
    assert as_json["UsernameToken"]["Password"] == "monty"
    assert as_json["ServiceAccessToken"]["AccessLicenseNumber"] == "123456789"


def test_from_env():
    os.environ["UPS_USERNAME"] = "eric.idle"
    os.environ["UPS_PASSWORD"] = "monty"
    os.environ["UPS_LICENSE"] = "123456789"
    credentials = UpsCredentials()
    assert credentials._username == "eric.idle"
    assert credentials._password == "monty"
    assert credentials._license == "123456789"
