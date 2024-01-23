"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass

from stokercloud.controller_data import PowerState, Unit, Value
from stokercloud.client import Client as StokerCloudClient

import datetime
from homeassistant.const import CONF_USERNAME, POWER_KILO_WATT, TEMP_CELSIUS, MASS_KILOGRAMS, LENGTH_CENTIMETERS
from .const import DOMAIN
from .mixins import StokerCloudControllerMixin

import logging

logger = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=1)


async def async_setup_entry(hass, config, async_add_entities):
    """Set up the sensor platform."""
    client = hass.data[DOMAIN][config.entry_id]
    serial = config.data[CONF_USERNAME]
    async_add_entities([
        StokerCloudControllerBinarySensor(client, serial, 'Running', 'running', 'power'),
        StokerCloudControllerBinarySensor(client, serial, 'Alarm', 'alarm', 'problem'),
        StokerCloudControllerSensor(client, serial, 'State', 'state'),
        StokerCloudControllerSensor(client, serial, 'Boiler Temperature', 'boiler_temperature_current',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Boiler Temperature Requested', 'boiler_temperature_requested',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Boiler Return Temperature', 'boiler_return_temperature',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Exhaust Temperature', 'exhaust_temmperature',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Hot Water Temperature', 'hotwater_temperature_current',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Hot Water Temperature Requested', 'hotwater_temperature_requested',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Outside Temperature', 'outside_temp',
                                    SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Wind Speed', 'wind_speed', SensorDeviceClass.WIND_SPEED),
        StokerCloudControllerSensor(client, serial, 'Wind Direction', 'wind_direction'),
        StokerCloudControllerSensor(client, serial, 'Humidity', 'humidity',
                                    SensorDeviceClass.HUMIDITY),

        StokerCloudControllerSensor(client, serial, 'Output Percent', 'output_percentage',
                                    SensorDeviceClass.PERCENT),
        StokerCloudControllerSensor(client, serial, 'Photosensor Percent', 'boiler_photosensor',
                                    SensorDeviceClass.PERCENT),      
        StokerCloudControllerSensor(client, serial, 'Boiler Power', 'boiler_power', SensorDeviceClass.POWER),
        StokerCloudControllerSensor(client, serial, 'Total Consumption', 'consumption_total',
                                    state_class=SensorStateClass.TOTAL_INCREASING),
        StokerCloudControllerSensor(client, serial, 'Daily Consumption', 'consumption_day', SensorDeviceClass.WEIGHT),
        StokerCloudControllerSensor(client, serial, 'Hopper Capacity', 'hopper_capacity', SensorDeviceClass.DISTANCE),
        StokerCloudControllerSensor(client, serial, 'Hopper Max Distance', 'hopper_max_distance', SensorDeviceClass.DISTANCE),
        StokerCloudControllerSensor(client, serial, 'Hopper Content', 'hopper_content', SensorDeviceClass.WEIGHT)
    ])


class StokerCloudControllerBinarySensor(StokerCloudControllerMixin, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, client: StokerCloudClient, serial, name: str, client_key: str, device_class):
        """Initialize the sensor."""
        super(StokerCloudControllerBinarySensor, self).__init__(client, serial, name, client_key)
        self._device_class = device_class

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._state is PowerState.ON

    @property
    def device_class(self):
        return self._device_class


class StokerCloudControllerSensor(StokerCloudControllerMixin, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, client: StokerCloudClient, serial, name: str, client_key: str, device_class=None,
                 state_class=None):
        """Initialize the sensor."""
        super(StokerCloudControllerSensor, self).__init__(client, serial, name, client_key)
        self._device_class = device_class
        self._attr_state_class = state_class

    @property
    def device_class(self):
        return self._device_class

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        if self._state:
            if isinstance(self._state, Value):
                return self._state.value
            return self._state

    @property
    def native_unit_of_measurement(self):
        if self._state and isinstance(self._state, Value):
            return {
                Unit.KWH: POWER_KILO_WATT,
                Unit.DEGREE: TEMP_CELSIUS,
                Unit.KILO_GRAM: MASS_KILOGRAMS,
                Unit.CM: LENGTH_CENTIMETERS,
            }.get(self._state.unit)
