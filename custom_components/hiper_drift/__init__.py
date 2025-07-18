"""The Hiper driftsstatus DK integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .component_api import ComponentApi
from .const import DOMAIN, LOGGER
from .hass_util import check_supress_config_update_listener


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class CommonData:
    """Common data."""

    component_api: ComponentApi
    coordinator: DataUpdateCoordinator


# The type alias needs to be suffixed with 'ConfigEntry'
type CommonConfigEntry = ConfigEntry[CommonData]


# ------------------------------------------------------------------
async def async_setup_entry(hass: HomeAssistant, entry: CommonConfigEntry) -> bool:
    """Set up Hiper driftsstatus DK from a config entry."""

    coordinator: DataUpdateCoordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name=DOMAIN,
    )

    component_api: ComponentApi = ComponentApi(
        hass,
        coordinator,
        entry,
        async_get_clientsession(hass),
    )

    entry.async_on_unload(entry.add_update_listener(config_update_listener))
    entry.runtime_data = CommonData(
        component_api=component_api,
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform.BINARY_SENSOR]
    )

    await coordinator.async_config_entry_first_refresh()

    return True


# ------------------------------------------------------------------
async def async_unload_entry(hass: HomeAssistant, entry: CommonConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(
        entry, [Platform.BINARY_SENSOR]
    )


# ------------------------------------------------------------------
async def async_reload_entry(hass: HomeAssistant, entry: CommonConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


# ------------------------------------------------------------------
@check_supress_config_update_listener()
async def config_update_listener(
    hass: HomeAssistant,
    config_entry: CommonConfigEntry,
) -> None:
    """Reload on config entry update."""

    # hmm: bool = hasattr(config_entry.runtime_data, "component_api")
    # dd = getattr(config_entry.runtime_data, "component_api")
    # hmm: bool = hasattr(dd, "_supress_update_listener")

    # if config_entry.runtime_data.component_api._supress_update_listener:
    #     config_entry.runtime_data.component_api._supress_update_listener = False
    #     return
    await hass.config_entries.async_reload(config_entry.entry_id)
