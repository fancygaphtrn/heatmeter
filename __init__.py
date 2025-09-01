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
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform
import voluptuous as vol
from homeassistant.const import (
        CONF_USERNAME, CONF_PASSWORD, CONF_HOST, CONF_PORT
    )

DOMAIN = 'heatmeter'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_PORT, default=80): cv.positive_int
    })
}, extra=vol.ALLOW_EXTRA)

ADMIN_URL = 'http://{0}:{1}/luci/admin/lm'
SET_URL = 'http://{0}:{1}/luci/;{2}/admin/lm/set?sp={3}'
TEMPERATURE_NAME = 'temperature'
TEMPERATURE_DEFAULT = '170'
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    _LOGGER.debug("Heatmeter init.py: config = %s", config[DOMAIN])

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][CONF_HOST] = config[DOMAIN][CONF_HOST]
    hass.data[DOMAIN][CONF_PORT] = config[DOMAIN][CONF_PORT]
    hass.data[DOMAIN][CONF_USERNAME] = config[DOMAIN][CONF_USERNAME]
    hass.data[DOMAIN][CONF_PASSWORD] = config[DOMAIN][CONF_PASSWORD]

    _LOGGER.debug("Heatmeter init.py: hass.data = %s", hass.data[DOMAIN])


    def handle_setpoint(call):
        """Handle the service call."""
        _LOGGER.debug("Heatmeter init.py: call = %s", call)
 
        temp = call.data.get(TEMPERATURE_NAME, TEMPERATURE_DEFAULT)
        _LOGGER.debug("Heatmeter init.py: temp = %s", temp)


        try:
            data = {'username':hass.data[DOMAIN][CONF_USERNAME], 
                'password':hass.data[DOMAIN][CONF_PASSWORD]}

            _LOGGER.debug("Heatmeter handle_setpoint: data = %s", data)

            url = ADMIN_URL.format(
                    hass.data[DOMAIN][CONF_HOST], hass.data[DOMAIN][CONF_PORT]
            )
            _LOGGER.debug("Heatmeter handle_setpoint: ADMIN_URL = %s", url)
            
            r = requests.post(url, data = data)
            if r.status_code == 200:
                _LOGGER.debug("Heatmeter handle_setpoint Status: %s" % (r.text))
                _LOGGER.debug("Heatmeter handle_setpoint headers: %s" % (r.headers))
    
                tokens = r.headers['set-cookie'].split(';')
                headers = {'Cookie': tokens[0] +';'}
                
                url = SET_URL.format(
                        hass.data[DOMAIN][CONF_HOST], hass.data[DOMAIN][CONF_PORT], tokens[2] , temp
                )
                _LOGGER.debug("Heatmeter handle_setpoint: SET_URL = %s", url)
                #url = 'http://smoker.lan/luci/;'+ tokens[2] + '/admin/lm/set?sp=' + temp
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    _LOGGER.info("Heatmeter handle_setpoint Setpoint updated: %s" % (temp))

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            _LOGGER.error("Heatmeter handle_setpoint Post Connection error %s" % (e))

    hass.services.register(DOMAIN, 'set_temperature', handle_setpoint)

    load_platform(hass, 'sensor', DOMAIN, {}, config)

    # Return boolean to indicate that initialization was successfully.
    return True
