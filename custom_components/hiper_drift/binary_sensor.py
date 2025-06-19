"""Support for Hiper."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CommonConfigEntry
from .component_api import ComponentApi, IssueItem
from .const import TRANSLATION_KEY, IssueType
from .entity import ComponentEntity
from .hass_util import object_to_state_attr_dict


# ------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CommonConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Entry for Hiper drift setup."""

    sensors = []

    sensors.append(HiperIssueBinarySensor(hass, entry, IssueType.REGIONAL))
    sensors.append(HiperIssueBinarySensor(hass, entry, IssueType.GENEREL))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class HiperIssueBinarySensor(ComponentEntity, BinarySensorEntity):
    """Sensor class Hiper."""

    _unrecorded_attributes = frozenset({MATCH_ALL})

    # ------------------------------------------------------
    def __init__(
        self,
        hass: HomeAssistant,
        entry: CommonConfigEntry,
        issue_type: IssueType,
    ) -> None:
        """Hiper issue sensor."""
        super().__init__(entry.runtime_data.coordinator, entry)
        self.hass: HomeAssistant = hass

        self.component_api: ComponentApi = entry.runtime_data.component_api

        if issue_type == IssueType.REGIONAL:
            self.component_api.async_write_ha_state_regional = self.async_write_ha_state
        else:
            self.component_api.async_write_ha_state_general = self.async_write_ha_state

        self.issue_type: IssueType = issue_type
        self._name = str(issue_type)
        self._unique_id = str(issue_type)

        self.translation_key = TRANSLATION_KEY
        self.dummy_attr = object_to_state_attr_dict(IssueItem())

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name.

        Returns:
            str: Name

        """
        return self._name

    # ------------------------------------------------------
    @property
    def is_on(self) -> bool:
        """Get the state."""

        if self.issue_type == IssueType.REGIONAL:
            if self.component_api.latest_issue_regional is None:
                return None
            return self.component_api.is_on_regional

        if self.component_api.latest_issue_general is None:
            return None
        return self.component_api.is_on_general

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """

        if self.issue_type == IssueType.REGIONAL:
            if not self.component_api.is_on_regional:
                return self.dummy_attr
            return object_to_state_attr_dict(self.component_api.latest_issue_regional)

        if not self.component_api.is_on_general:
            return self.dummy_attr

        return object_to_state_attr_dict(self.component_api.latest_issue_general)

    # ------------------------------------------------------
    @property
    def unique_id(self) -> str:
        """Unique id.

        Returns:
            str: Unique id

        """
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
