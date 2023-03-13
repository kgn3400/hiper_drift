"""Support for Hiper."""
from __future__ import annotations

from homeassistant.components.sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .entity import HiperDriftEntity
from .hiper_api import HiperApi


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup for Hiper"""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hiper_api: HiperApi = hass.data[DOMAIN][entry.entry_id]["hiper_api"]

    sensors = []

    sensors.append(HiperMsgSensor(coordinator, entry, hiper_api))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class HiperMsgSensor(HiperDriftEntity, SensorEntity):
    """Sensor class Hiper"""

    # ------------------------------------------------------
    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        hiper_api: HiperApi,
    ) -> None:
        super().__init__(coordinator, entry)

        self.hiper_api = hiper_api
        self.coordinator = coordinator
        self._name = "Message"
        self._unique_id = "message"

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        return self._name

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        return "mdi:message-reply-outline"

    # ------------------------------------------------------
    @property
    def native_value(self) -> str | None:
        return self.hiper_api.msg

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        attr: dict = {}

        return attr

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        return self._unique_id

    # ------------------------------------------------------
    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    # ------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    # ------------------------------------------------------
    async def async_update(self) -> None:
        """Update the entity. Only used by the generic entity update service."""
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
