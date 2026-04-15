"""Tests for Tankerkönig Sensor."""

import json

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import CURRENCY_EURO
import pytest
import requests
import requests_mock

from custom_components.tankerkoenig.sensor import TankerkoenigApi, TankerkoenigSensor


@pytest.mark.parametrize(
    "api_response",
    [
        None,
        "",
        {},
        {"stations": None},
        {"stations": {}},
    ],
)
def test_sensor_with_empty_response(api_response, requests_mock: requests_mock.Mocker):
    """Test that sensor with empty response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text=json.dumps(api_response),
    )
    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state is None
    assert sensor.extra_state_attributes.get("brand") is None
    assert sensor.extra_state_attributes.get("address") is None
    assert sensor.extra_state_attributes.get("status") is None
    assert sensor.extra_state_attributes.get("latitude") is None
    assert sensor.extra_state_attributes.get("longitude") is None
    assert sensor.extra_state_attributes.get("attribution") is None


def test_sensor_with_malformed_response(
    create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with malformed response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text="some text",
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state is None
    assert sensor.extra_state_attributes.get("brand") is None
    assert sensor.extra_state_attributes.get("address") is None
    assert sensor.extra_state_attributes.get("status") is None
    assert sensor.extra_state_attributes.get("latitude") is None
    assert sensor.extra_state_attributes.get("longitude") is None
    assert sensor.extra_state_attributes.get("attribution") is None


def test_sensor_with_error_response(
    create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with error response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        status_code=500,
        text="some error",
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state is None
    assert sensor.extra_state_attributes.get("brand") is None
    assert sensor.extra_state_attributes.get("address") is None
    assert sensor.extra_state_attributes.get("status") is None
    assert sensor.extra_state_attributes.get("latitude") is None
    assert sensor.extra_state_attributes.get("longitude") is None
    assert sensor.extra_state_attributes.get("attribution") is None


def test_sensor_with_no_response(
    create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with no response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        exc=requests.exceptions.ConnectionError,
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state is None
    assert sensor.extra_state_attributes.get("brand") is None
    assert sensor.extra_state_attributes.get("address") is None
    assert sensor.extra_state_attributes.get("status") is None
    assert sensor.extra_state_attributes.get("latitude") is None
    assert sensor.extra_state_attributes.get("longitude") is None
    assert sensor.extra_state_attributes.get("attribution") is None


def test_sensor_with_malformed_station(
    create_station, create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with malformed station returns correct properties."""
    station = (
        create_station()
        .with_brand("  Demo Oil  ")
        .with_street("  Demo street  ")
        .with_house_number(" 1a ")
        .with_latitude(52.53083)
        .with_longitude(13.440946)
        .with_is_open(True)
        .with_price(1.825)
        .build()
    )

    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text=create_api_response([station]),
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state == 1.825
    assert sensor.extra_state_attributes.get("brand") == "Demo Oil"
    assert sensor.extra_state_attributes.get("address") == "Demo Street 1a"
    assert sensor.extra_state_attributes.get("status") == "open"
    assert sensor.extra_state_attributes.get("latitude") == 52.53083
    assert sensor.extra_state_attributes.get("longitude") == 13.440946
    assert (
        sensor.extra_state_attributes.get("attribution")
        == "Data provided by Tankerkönig"
    )


def test_sensor_with_opened_station(
    create_station, create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with opened station returns correct properties."""
    station = (
        create_station()
        .with_brand("Demo Oil")
        .with_street("Demo street")
        .with_house_number("1a")
        .with_latitude(52.53083)
        .with_longitude(13.440946)
        .with_is_open(True)
        .with_price(1.825)
        .build()
    )

    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text=create_api_response([station]),
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state == 1.825
    assert sensor.extra_state_attributes.get("brand") == "Demo Oil"
    assert sensor.extra_state_attributes.get("address") == "Demo Street 1a"
    assert sensor.extra_state_attributes.get("status") == "open"
    assert sensor.extra_state_attributes.get("latitude") == 52.53083
    assert sensor.extra_state_attributes.get("longitude") == 13.440946
    assert (
        sensor.extra_state_attributes.get("attribution")
        == "Data provided by Tankerkönig"
    )


def test_sensor_with_closed_station(
    create_station, create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with closed station returns correct properties."""
    station = (
        create_station()
        .with_brand("Demo Oil")
        .with_street("Demo street")
        .with_house_number("1a")
        .with_latitude(52.53083)
        .with_longitude(13.440946)
        .with_is_open(False)
        .with_price(1.825)
        .build()
    )

    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text=create_api_response([station]),
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state == 1.825
    assert sensor.extra_state_attributes.get("brand") == "Demo Oil"
    assert sensor.extra_state_attributes.get("address") == "Demo Street 1a"
    assert sensor.extra_state_attributes.get("status") == "closed"
    assert sensor.extra_state_attributes.get("latitude") == 52.53083
    assert sensor.extra_state_attributes.get("longitude") == 13.440946
    assert (
        sensor.extra_state_attributes.get("attribution")
        == "Data provided by Tankerkönig"
    )


def test_sensor_with_multiple_stations(
    create_station, create_api_response, requests_mock: requests_mock.Mocker
):
    """Test that sensor with multiple stations returns correct properties."""
    station_first = (
        create_station()
        .with_brand("Demo Oil First")
        .with_street("Demo street first")
        .with_house_number("1a")
        .with_latitude(52.53083)
        .with_longitude(13.440946)
        .with_is_open(False)
        .with_price(2.825)
        .build()
    )
    station_second = (
        create_station()
        .with_brand("Demo Oil Second")
        .with_street("Demo street second")
        .with_house_number("1b")
        .with_latitude(52.53083)
        .with_longitude(13.440946)
        .with_is_open(True)
        .with_price(3.825)
        .build()
    )

    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text=create_api_response([station_first, station_second]),
    )

    api = TankerkoenigApi("some-api-key")
    sensor = TankerkoenigSensor(api, "Sensor", "5.0", "5.0", 1.5, "diesel")

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == CURRENCY_EURO
    assert sensor.state == 2.825
    assert sensor.extra_state_attributes.get("brand") == "Demo Oil First"
    assert sensor.extra_state_attributes.get("address") == "Demo Street First 1a"
    assert sensor.extra_state_attributes.get("status") == "closed"
    assert sensor.extra_state_attributes.get("latitude") == 52.53083
    assert sensor.extra_state_attributes.get("longitude") == 13.440946
    assert (
        sensor.extra_state_attributes.get("attribution")
        == "Data provided by Tankerkönig"
    )
