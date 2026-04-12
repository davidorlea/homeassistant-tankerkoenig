"""Test fixtures for Tankerkönig Sensor."""

import json
from typing import Self

from pytest import fixture


class TankerkoenigStationFixture:
    """Representation of a Tankerkönig station fixture."""

    def __init__(self):
        """Initialize the Tankerkönig station fixture."""
        self._brand = "Some Brand"
        self._street = "Some Street"
        self._house_number = "Some House Number"
        self._latitude = 0.00000
        self._longitude = 0.00000
        self._is_open = True
        self._price = 1.234

    def with_brand(self, brand: str) -> Self:
        """Set an individual brand."""
        self._brand = brand
        return self

    def with_street(self, street: str) -> Self:
        """Set an individual street."""
        self._street = street
        return self

    def with_house_number(self, house_number: str) -> Self:
        """Set an individual house number."""
        self._house_number = house_number
        return self

    def with_latitude(self, latitude: float) -> Self:
        """Set an individual latitude."""
        self._latitude = latitude
        return self

    def with_longitude(self, longitude: float) -> Self:
        """Set an individual longitude."""
        self._longitude = longitude
        return self

    def with_is_open(self, is_open: bool) -> Self:
        """Set an individual open status."""
        self._is_open = is_open
        return self

    def with_price(self, price: float) -> Self:
        """Set an individual price."""
        self._price = price
        return self

    def build(self) -> dict:
        """Return the station."""
        return {
            "brand": self._brand,
            "street": self._street,
            "houseNumber": self._house_number,
            "lat": self._latitude,
            "lng": self._longitude,
            "isOpen": self._is_open,
            "price": self._price,
        }


class TankerkoenigStationsFixture:
    """Representation of a Tankerkoenig API fixture."""

    def __init__(self):
        """Initialize the Tankerkoenig API fixture."""
        self._stations = []

    def with_stations(self, stations: [dict]) -> Self:
        """Set a list of stations."""
        self._stations = stations
        return self

    def build(self) -> dict:
        """Return the stations."""
        return {"stations": self._stations}


@fixture()
def create_station():
    """Fixture to create a Tankerkönig station."""

    def _create_station():
        return TankerkoenigStationFixture()

    return _create_station


@fixture()
def create_api_response():
    """Fixture to create a Tankerkönig API response."""

    def _create_api_response(stations: [dict]):
        stations = TankerkoenigStationsFixture().with_stations(stations).build()
        return json.dumps(stations)

    return _create_api_response
