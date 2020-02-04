"""Representation of Tankerkönig Sensors."""

from datetime import timedelta
import json
import logging

import voluptuous as vol

from homeassistant.components.rest.sensor import RestData
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    CONF_API_KEY,
    CONF_NAME,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=10)

FUEL_TYPES = {"e5", "e10", "diesel"}

CONF_FUEL_TYPE = "fuel_type"
CONF_RADIUS = "radius"

DEFAULT_NAME = "Tankerkoenig"
DEFAULT_RADIUS = 1.5

ATTR_BRAND = "brand"
ATTR_ADDRESS = "address"
ATTR_STATUS = "status"

UNIT_OF_MEASUREMENT = "€"
ICON = "mdi:gas-station"
ATTRIBUTION = "Data provided by Tankerkönig"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_KEY): cv.string,
        vol.Required(CONF_FUEL_TYPE): vol.All(cv.string, vol.In(FUEL_TYPES)),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS): cv.Number,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""

    api_key = config.get(CONF_API_KEY)
    fuel_type = config.get(CONF_FUEL_TYPE)
    name = config.get(CONF_NAME)
    radius = config.get(CONF_RADIUS)

    latitude = hass.config.latitude
    longitude = hass.config.longitude

    url = "https://creativecommons.tankerkoenig.de/json/list.php?lat={}&lng={}&rad={}&sort=price&type={}&apikey={}"
    endpoint = url.format(latitude, longitude, radius, fuel_type, api_key)
    rest = RestData("GET", endpoint, None, None, None, True)

    add_entities([TankerkoenigSensor(rest, name)])


class TankerkoenigSensor(Entity):
    """Representation of a Tankerkönig Sensor."""

    def __init__(self, rest, name):
        """Initialize the Tankerkönig Sensor."""
        self.rest = rest
        self._name = name
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the Tankerkönig Sensor."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of the Tankerkönig Sensor."""
        return UNIT_OF_MEASUREMENT

    @property
    def icon(self):
        """Icon to use in the frontend of the Tankerkönig Sensor."""
        return ICON

    @property
    def state(self):
        """Return the state of the Tankerkönig Sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the Tankerkönig Sensor.."""
        return self._attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Fetch new state data for the Tankerkönig Sensor."""
        self._state = None
        self._attributes = {}

        self.rest.update()
        result = self.rest.data
        stations = []

        if result:
            try:
                json_result = json.loads(result)
                if json_result["ok"]:
                    stations = json_result["stations"]
                    _LOGGER.debug("Received stations: %s", stations)
            except ValueError:
                _LOGGER.warning("REST result could not be parsed as JSON")
                _LOGGER.debug("Erroneous JSON: %s", result)
        else:
            _LOGGER.warning("Empty reply found when expecting JSON data")

        if stations:
            self._state = stations[0]["price"]
            self._attributes[ATTR_BRAND] = stations[0]["brand"].title()
            self._attributes[ATTR_ADDRESS] = (
                stations[0]["street"].title() + stations[0]["houseNumber"]
            )
            self._attributes[ATTR_STATUS] = (
                "open" if stations[0]["isOpen"] else "closed"
            )
            self._attributes[ATTR_LATITUDE] = stations[0]["lat"]
            self._attributes[ATTR_LONGITUDE] = stations[0]["lng"]
            self._attributes[ATTR_ATTRIBUTION] = ATTRIBUTION
