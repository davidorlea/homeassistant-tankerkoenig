"""Test fixtures for Tankerkönig Sensor."""

from collections.abc import Callable
import json
from typing import Any, Self

from pytest import fixture


class TankerkoenigStationFixture:
    """Representation of a Tankerkönig station fixture."""

    def __init__(self) -> None:
        """Initialize the Tankerkönig station fixture."""
        self._brand: str = "Some Brand"
        self._street: str = "Some Street"
        self._house_number: str = "Some House Number"
        self._latitude: float = 0.00000
        self._longitude: float = 0.00000
        self._is_open: bool = True
        self._price: float = 1.234

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

    def build(self) -> dict[str, Any]:
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

    def __init__(self) -> None:
        """Initialize the Tankerkoenig API fixture."""
        self._stations: list[dict[str, Any]] = []

    def with_stations(self, stations: list[dict[str, Any]]) -> Self:
        """Set a list of stations."""
        self._stations = stations
        return self

    def build(self) -> dict[str, Any]:
        """Return the stations."""
        return {"stations": self._stations}


@fixture()
def create_station() -> Callable[[], TankerkoenigStationFixture]:
    """Fixture to create a Tankerkönig station."""

    def _create_station() -> TankerkoenigStationFixture:
        return TankerkoenigStationFixture()

    return _create_station


@fixture()
def create_api_response() -> Callable[[list[dict[str, Any]]], str]:
    """Fixture to create a Tankerkönig API response."""

    def _create_api_response(stations: list[dict[str, Any]]) -> str:
        response = TankerkoenigStationsFixture().with_stations(stations).build()
        return json.dumps(response)

    return _create_api_response
