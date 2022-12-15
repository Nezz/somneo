"""Platform for number entity to catch hour/minute of alarms."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.input_datetime import InputDatetime, CONF_HAS_DATE, CONF_HAS_TIME
from homeassistant.components.number import NumberEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ALARMS_ICON
from .entity import SomneoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, 
    config_entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback,
) -> None:
    """ Add Somneo from config_entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    unique_id = config_entry.unique_id
    assert unique_id is not None
    name = config_entry.data[CONF_NAME]
    device_info = config_entry.data['dev_info']  

    alarms = []
    # Add hour & min number_entity for each alarms
    for alarm in list(coordinator.data['alarms']):
        alarms.append(SomneoTime(coordinator, unique_id, name, device_info, alarm))
    
    snooze = [SomneoSnooze(coordinator, unique_id, name, device_info, 'snooze')]

    async_add_entities(alarms, True)
    async_add_entities(snooze, True)

class SomneoTime(SomneoEntity, InputDatetime):
    _attr_should_poll = True
    _attr_icon = ALARMS_ICON
    editable = True

    def __init__(self, coordinator, unique_id, name, dev_info, alarm):
        """Initialize number entities."""
        SomneoEntity.__init__(self, coordinator, unique_id, name, dev_info, alarm)
        InputDatetime.__init__(self, { CONF_HAS_DATE: False, CONF_HAS_TIME: True })

        self._attr_name = alarm.capitalize()

        self._alarm = alarm

    @property
    def unique_id(self) -> str | None:
        return self._attr_unique_id

    @property
    def state(self):
        return f"self.coordinator.data['alarms_hour'][self._alarm]:{self.coordinator.data['alarms_minute'][self._alarm]:02d}"

    @callback
    def async_set_datetime(self, date=None, time=None, datetime=None, timestamp=None):
        self.coordinator.async_set_alarm(self._alarm, hours = time.hour, minutes = time.minute)


class SomneoSnooze(SomneoEntity, NumberEntity):
    _attr_should_poll = True
    _attr_available = True
    _attr_assumed_state = False
    _attr_name = 'Snooze time'
    _attr_native_min_value = 1
    _attr_native_max_value = 20
    _attr_native_step = 1
    _attr_icon = 'hass:alarm-snooze'

    @property
    def native_value(self) -> int:
        return self.coordinator.data['snooze_time']

    async def async_set_native_value(self, value: float) -> None:
        """Called when user adjust snooze time in the UI"""
        await self.coordinator.async_set_snooze_time(int(value))