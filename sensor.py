"""
Support for reading Heatmeter data. See https://store.heatermeter.com/

configuration.yaml

heatmeter:
    host: smoker.lan
    port: 80
    username: PORTAL_LOGIN
    password: PORTAL_PASSWORD
    scan_interval: 2
"""
import logging
import requests
import json
from datetime import timedelta
import homeassistant.util.dt as dt_util
import voluptuous as vol

from homeassistant.helpers.config_validation import (  # noqa
    PLATFORM_SCHEMA, PLATFORM_SCHEMA_BASE)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
        CONF_USERNAME, CONF_PASSWORD, CONF_HOST, CONF_PORT,
        CONF_RESOURCES,TEMP_FAHRENHEIT
    )
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

ENTITY_ID_FORMAT = DOMAIN + '.{}'

BASE_URL = 'http://{0}:{1}{2}'
SCAN_INTERVAL = timedelta(seconds=2)
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=2)

SENSOR_TYPES = {
    'setpoint': ['Setpoint', TEMP_FAHRENHEIT, 'mdi:thermometer'],
    'lid': ['Lid', '', 'mdi:fridge'],
    'fan': ['Fan', '%', 'mdi:fan'],
    'probe0_temperature': ['Probe0 Temperature', TEMP_FAHRENHEIT, 'mdi:thermometer'],
    'probe1_temperature': ['Probe1 Temperature', TEMP_FAHRENHEIT, 'mdi:thermometer'],
    'probe2_temperature': ['Probe2 Temperature', TEMP_FAHRENHEIT, 'mdi:thermometer'],
    'probe3_temperature': ['Probe3 Temperature', TEMP_FAHRENHEIT, 'mdi:thermometer']
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Heatmeter sensors."""
    
    _LOGGER.debug("Heatmeter: config = %s", config)
    _LOGGER.debug("Heatmeter: hass.data = %s", hass.data[DOMAIN])
    _LOGGER.debug("Heatmeter: hass = %s", hass)
    _LOGGER.debug("Heatmeter: discovery_info = %s", discovery_info)
       
    host = hass.data[DOMAIN][CONF_HOST]
    port = hass.data[DOMAIN][CONF_PORT]
    username = hass.data[DOMAIN][CONF_USERNAME]
    password = hass.data[DOMAIN][CONF_PASSWORD]
    
    try:
        data = HeatmeterData(host, port, username, password)
    except RunTimeError:
        _LOGGER.error("Heatmeter: Unable to connect fetch data from Heatmeter %s:%s",
                      host, port)
        return False

    entities = []

    for resource in SENSOR_TYPES:
        sensor_type = resource.lower()

        entities.append(HeatmeterSensor(data, sensor_type))
    
    _LOGGER.debug("Heatmeter: entities = %s", entities)
    add_entities(entities)


# pylint: disable=abstract-method
class HeatmeterData(object):
    """Representation of a Heatmeter."""

    def __init__(self, host, port, username, password):
        """Initialize the Heatmeter."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.data = None
        self._backoff = dt_util.utcnow()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the Heatmeter."""

        _LOGGER.debug("Heatmeter: Backoff = %i", self._backoff - dt_util.utcnow())
        if self._backoff > dt_util.utcnow():
            return

        dataurl = BASE_URL.format(
                    self._host, self._port,
                    '/luci/lm/hmstatus'
        )
        try:
            response = requests.get(dataurl, timeout=5)
            self.data = response.json()
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Heatmeter: No route to device %s", dataurl)
            self.data = None
            self._backoff = dt_util.utcnow() + timedelta(seconds=60)
            
        _LOGGER.debug("Heatmeter: Data = %s", self.data)


class HeatmeterSensor(Entity):
    """Representation of a Heatmeter sensor from the Heatmeter."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self.entity_id = ENTITY_ID_FORMAT.format(sensor_type)
        self._name = SENSOR_TYPES[self.type][0]
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        _LOGGER.debug("Heatmeter: SensorData = %s", self.data.data)
        _LOGGER.debug("Heatmeter: type = %s", self.type)
        
        if self.data.data == None:
            self._state = "Unknown"
        else:
            if self.type == 'setpoint':
                self._state = self.data.data["set"]
            if self.type == 'fan':
                self._state = self.data.data["fan"]["c"]
            if self.type == 'lid':
                if self.data.data["lid"] == 0:
                    self._state =  "Closed"
                else:
                    self._state =  "Open"
            if self.type == 'probe0_temperature':
                self._state = self.data.data["temps"][0]["c"]
                self._name = self.data.data["temps"][0]["n"]
            if self.type == 'probe1_temperature':
                self._state = self.data.data["temps"][1]["c"]
                self._name = self.data.data["temps"][1]["n"]
            if self.type == 'probe2_temperature':
                self._state = self.data.data["temps"][2]["c"]
                self._name = self.data.data["temps"][2]["n"]
            if self.type == 'probe3_temperature':
                self._state = self.data.data["temps"][3]["c"]
                self._name = self.data.data["temps"][3]["n"]
