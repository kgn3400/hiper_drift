"""Services for Hiper integration."""
from homeassistant.core import HomeAssistant

from .component_api import ComponentApi
from .const import DOMAIN


async def async_setup_services(
    hass: HomeAssistant, component_api: ComponentApi
) -> None:
    """Set up the services for the Hiper integration."""

    hass.services.async_register(DOMAIN, "update", component_api.update_service)
