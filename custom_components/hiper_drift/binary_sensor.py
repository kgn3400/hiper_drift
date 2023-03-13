"""Support for Hiper dK."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """ddf f"""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    hiper_api: HiperApi = hass.data[DOMAIN][entry.entry_id]["hiper_api"]

    sensors = []

    sensors.append(HiperBinarySensor(coordinator, entry, hiper_api))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class HiperBinarySensor(HiperDriftEntity, BinarySensorEntity):
    """Sensor class for Hiper"""

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

        self._name = "Status"
        self._unique_id = "status"

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        return self._name

    # ------------------------------------------------------
    @property
    def icon(self) -> str:
        return "mdi:ip-network"

    # ------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """Get the state."""

        return self.hiper_api.is_on

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        attr: dict = {}

        attr["message"] = self.hiper_api.msg

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
