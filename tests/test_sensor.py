"""Tests for Tankerkönig Sensor."""

from collections.abc import Mapping
import json
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass
import pytest
import requests
import requests_mock

from custom_components.tankerkoenig.sensor import TankerkoenigApi, TankerkoenigSensor


def extra_state_attributes(sensor: TankerkoenigSensor) -> Mapping[str, Any]:
    """Return sensor attributes with a non-optional type for assertions."""
    assert sensor.extra_state_attributes is not None
    return sensor.extra_state_attributes


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
def test_sensor_with_empty_response(
    api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
    """Test that sensor with empty response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text=json.dumps(api_response),
    )
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state is None
    sensor_attributes = extra_state_attributes(sensor)
    assert "brand" not in sensor_attributes
    assert "address" not in sensor_attributes
    assert "status" not in sensor_attributes
    assert "latitude" not in sensor_attributes
    assert "longitude" not in sensor_attributes
    assert "attribution" not in sensor_attributes


def test_sensor_with_malformed_response(
    create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
    """Test that sensor with malformed response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        text="some text",
    )
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state is None
    sensor_attributes = extra_state_attributes(sensor)
    assert "brand" not in sensor_attributes
    assert "address" not in sensor_attributes
    assert "status" not in sensor_attributes
    assert "latitude" not in sensor_attributes
    assert "longitude" not in sensor_attributes
    assert "attribution" not in sensor_attributes


def test_sensor_with_error_response(
    create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
    """Test that sensor with error response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        status_code=500,
        text="some error",
    )
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state is None
    sensor_attributes = extra_state_attributes(sensor)
    assert "brand" not in sensor_attributes
    assert "address" not in sensor_attributes
    assert "status" not in sensor_attributes
    assert "latitude" not in sensor_attributes
    assert "longitude" not in sensor_attributes
    assert "attribution" not in sensor_attributes


def test_sensor_with_no_response(
    create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
    """Test that sensor with no response returns correct properties."""
    requests_mock.get(
        "https://creativecommons.tankerkoenig.de/json/list.php",
        exc=requests.exceptions.ConnectionError,
    )
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state is None
    sensor_attributes = extra_state_attributes(sensor)
    assert "brand" not in sensor_attributes
    assert "address" not in sensor_attributes
    assert "status" not in sensor_attributes
    assert "latitude" not in sensor_attributes
    assert "longitude" not in sensor_attributes
    assert "attribution" not in sensor_attributes


def test_sensor_with_malformed_station(
    create_station: Any, create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
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
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state == 1.825
    sensor_attributes = extra_state_attributes(sensor)
    assert sensor_attributes["brand"] == "Demo Oil"
    assert sensor_attributes["address"] == "Demo Street 1a"
    assert sensor_attributes["status"] == "open"
    assert sensor_attributes["latitude"] == 52.53083
    assert sensor_attributes["longitude"] == 13.440946
    assert "attribution" not in sensor_attributes


def test_sensor_with_opened_station(
    create_station: Any, create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
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
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state == 1.825
    sensor_attributes = extra_state_attributes(sensor)
    assert sensor_attributes["brand"] == "Demo Oil"
    assert sensor_attributes["address"] == "Demo Street 1a"
    assert sensor_attributes["status"] == "open"
    assert sensor_attributes["latitude"] == 52.53083
    assert sensor_attributes["longitude"] == 13.440946
    assert "attribution" not in sensor_attributes


def test_sensor_with_closed_station(
    create_station: Any, create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
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
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state == 1.825
    sensor_attributes = extra_state_attributes(sensor)
    assert sensor_attributes["brand"] == "Demo Oil"
    assert sensor_attributes["address"] == "Demo Street 1a"
    assert sensor_attributes["status"] == "closed"
    assert sensor_attributes["latitude"] == 52.53083
    assert sensor_attributes["longitude"] == 13.440946
    assert "attribution" not in sensor_attributes


def test_sensor_with_multiple_stations(
    create_station: Any, create_api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
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
    sensor = TankerkoenigSensor(
        TankerkoenigApi("some-api-key"), "Sensor", 5.0, 5.0, 1.5, "diesel"
    )

    sensor.update()

    assert sensor.name == "Sensor"
    assert sensor.icon == "mdi:gas-station"
    assert sensor.device_class == SensorDeviceClass.MONETARY
    assert sensor.unit_of_measurement == "€"
    assert sensor.attribution == "Data provided by Tankerkönig"
    assert sensor.state == 2.825
    sensor_attributes = extra_state_attributes(sensor)
    assert sensor_attributes["brand"] == "Demo Oil First"
    assert sensor_attributes["address"] == "Demo Street First 1a"
    assert sensor_attributes["status"] == "closed"
    assert sensor_attributes["latitude"] == 52.53083
    assert sensor_attributes["longitude"] == 13.440946
    assert "attribution" not in sensor_attributes
