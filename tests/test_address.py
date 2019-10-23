import pytest

from ups import Address


@pytest.fixture()
def white_house():
    return Address(
        address="1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zip="20500",
    )


def test_address_create():
    address = Address(
        address="1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zip="20500",
    )
    assert address.address == "1600 Pennsylvania Avenue NW"
    assert address.city == "Washington"
    assert address.state == "DC"
    assert address.zip == "20500"


def test_from_str(white_house):
    address = Address.from_str("1600 Pennsylvania Avenue NW, Washington, DC, 20500")
    assert address == white_house

    address = Address.from_str('"1600 Pennsylvania Avenue NW, POTUS", Washington, DC, 20500')
    assert address.address == "1600 Pennsylvania Avenue NW, POTUS"
    assert address.city == "Washington"
    assert address.state == "DC"
    assert address.zip == "20500"


def test_to_str():
    address = Address(
        address="1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zip="20500",
    )
    assert str(address) == "1600 Pennsylvania Avenue NW,Washington,DC,20500"
    address = Address(
        address="1600 Pennsylvania Avenue NW, POTUS",
        city="Washington",
        state="DC",
        zip="20500",
    )
    assert str(address) == '"1600 Pennsylvania Avenue NW, POTUS",Washington,DC,20500'


@pytest.mark.parametrize("zip", (20500, "20500"))
def test_zip_types(zip):
    address = Address(
        address="1600 Pennsylvania Avenue NW",
        city="Washington",
        state="DC",
        zip=zip,
    )
    assert address.zip == str(zip)


def test_as_dict(white_house):
    assert Address(**white_house.as_dict()) == white_house


def test_items(white_house):
    assert white_house.items() == (
        ("address", white_house.address),
        ("city", white_house.city),
        ("state", white_house.state),
        ("zip", white_house.zip),
    )
    assert Address(**dict(white_house.items())) == white_house
