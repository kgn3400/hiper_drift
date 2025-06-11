"""Support for Hiper."""

from __future__ import annotations

from homeassistant.components.sensor import (  # SensorDeviceClass,; SensorEntityDescription,
    SensorEntity,
)
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CommonConfigEntry
from .component_api import ComponentApi
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

    sensors.append(HiperIssueSensor(hass, entry, IssueType.REGIONAL))
    sensors.append(HiperIssueSensor(hass, entry, IssueType.GENEREL))

    async_add_entities(sensors)


# ------------------------------------------------------
# ------------------------------------------------------
class HiperIssueSensor(ComponentEntity, SensorEntity):
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
        self.issue_type: IssueType = issue_type
        self._name = str(issue_type)
        self._unique_id = str(issue_type)

        self.translation_key = TRANSLATION_KEY

    # ------------------------------------------------------
    @property
    def name(self) -> str:
        """Name.

        Returns:
            str: Name

        """
        return self._name

    @property
    def native_value(self) -> str | None:
        """Native value.

        Returns:
            str | None: Native value

        """

        if self.issue_type == IssueType.REGIONAL:
            if self.component_api.issue_regional is None:
                return None
            return self.component_api.issue_regional.text[:255]

        if self.component_api.issue_general is None:
            return None
        return self.component_api.issue_general.text[:255]

    # ------------------------------------------------------
    @property
    def extra_state_attributes(self) -> dict:
        """Extra state attributes.

        Returns:
            dict: Extra state attributes

        """

        if self.issue_type == IssueType.REGIONAL:
            return object_to_state_attr_dict(self.component_api.issue_regional)

        return object_to_state_attr_dict(self.component_api.issue_general)

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
