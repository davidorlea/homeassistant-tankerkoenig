"""Representation of Tankerkönig Sensors."""

from datetime import timedelta
import logging
from typing import Any, cast

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    CONF_API_KEY,
    CONF_NAME,
    CURRENCY_EURO,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle
import requests
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=10)

FUEL_TYPES = {"diesel", "e5", "e10"}

CONF_FUEL_TYPE = "fuel_type"
CONF_RADIUS = "radius"

DEFAULT_NAME = "Tankerkoenig"
DEFAULT_RADIUS = 1.5

ATTR_BRAND = "brand"
ATTR_ADDRESS = "address"
ATTR_STATUS = "status"

ICON = "mdi:gas-station"
ATTRIBUTION = "Data provided by Tankerkönig"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_FUEL_TYPE): vol.All(cv.string, vol.In(FUEL_TYPES)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): cv.positive_float,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    api_key: str = config[CONF_API_KEY]
    fuel_type: str = config[CONF_FUEL_TYPE]
    name: str = config[CONF_NAME]
    radius: float = config[CONF_RADIUS]

    latitude: float = hass.config.latitude
    longitude: float = hass.config.longitude

    api: TankerkoenigApi = TankerkoenigApi(api_key)
    add_entities(
        [TankerkoenigSensor(api, name, latitude, longitude, radius, fuel_type)]
    )


class TankerkoenigApi:
    """Representation of the Tankerkönig API."""

    def __init__(self, api_key: str) -> None:
        """Initialize the Tankerkönig API."""
        self._api_key: str = api_key

    def get_stations(
        self,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> dict[str, Any] | None:
        """Get stations matching a perimeter and fuel type from the Tankerkönig API."""
        resource = (
            f"https://creativecommons.tankerkoenig.de/json/list.php"
            f"?apikey={self._api_key}"
            f"&lat={latitude}"
            f"&lng={longitude}"
            f"&rad={radius}"
            f"&type={fuel_type}"
            f"&sort=price"
        )
        try:
            response = requests.get(resource, verify=True, timeout=(5, 10))
            response.raise_for_status()
            return cast(dict[str, Any], response.json())
        except requests.exceptions.JSONDecodeError as ex:
            _LOGGER.error("Error parsing data: %s failed with %s", resource, ex)
            return None
        except requests.exceptions.HTTPError as ex:
            error_response = ex.response
            if error_response is not None and error_response.status_code >= 500:
                _LOGGER.debug("Error fetching data: %s failed with %s", resource, ex)
            else:
                _LOGGER.error("Error fetching data: %s failed with %s", resource, ex)
            return None
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as ex:
            _LOGGER.debug("Error fetching data: %s failed with %s", resource, ex)
            return None
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error fetching data: %s failed with %s", resource, ex)
            return None


class TankerkoenigSensor(SensorEntity):
    """Representation of a Tankerkönig Sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_icon = ICON
    _attr_native_unit_of_measurement = CURRENCY_EURO

    def __init__(
        self,
        api: TankerkoenigApi,
        name: str,
        latitude: float,
        longitude: float,
        radius: float,
        fuel_type: str,
    ) -> None:
        """Initialize the Tankerkönig Sensor."""
        self._api: TankerkoenigApi = api
        self._attr_name = name
        self._latitude: float = latitude
        self._longitude: float = longitude
        self._radius: float = radius
        self._fuel_type: str = fuel_type
        self._attr_native_value: float | None = None
        self._attr_extra_state_attributes: dict[str, Any] = {}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        """Fetch new state data for the Tankerkönig Sensor."""
        self._attr_native_value = None
        self._attr_extra_state_attributes = {}

        result: dict[str, Any] | None = self._api.get_stations(
            self._latitude, self._longitude, self._radius, self._fuel_type
        )
        stations: list[dict[str, Any]] | None = None

        if result:
            try:
                stations = result["stations"]
            except (KeyError, TypeError) as ex:
                _LOGGER.error(
                    "Erroneous result found: %s failed with %s",
                    result,
                    ex,
                )

        if stations:
            self._attr_native_value = stations[0]["price"]
            self._attr_extra_state_attributes[ATTR_BRAND] = (
                stations[0]["brand"].title().strip()
            )
            self._attr_extra_state_attributes[ATTR_ADDRESS] = (
                f"{stations[0]['street'].title().strip()} {stations[0]['houseNumber'].strip()}"
            )
            self._attr_extra_state_attributes[ATTR_STATUS] = (
                "open" if stations[0]["isOpen"] else "closed"
            )
            self._attr_extra_state_attributes[ATTR_LATITUDE] = stations[0]["lat"]
            self._attr_extra_state_attributes[ATTR_LONGITUDE] = stations[0]["lng"]
