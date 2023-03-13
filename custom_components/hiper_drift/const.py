"""Constants for Hiper driftsstatus DK integration."""
from logging import Logger, getLogger

DOMAIN = "hiper_drift"
DOMAIN_NAME = "Hiper drift"
LOGGER: Logger = getLogger(__name__)

CONF_REGION: str = "region"
CONF_CITY: str = "city"
CONF_CITY_CHECK: str = "city_check"
CONF_STREET: str = "street"
CONF_STREET_CHECK: str = "street_check"
CONF_GENERAL_MSG: str = "general_msg"
CONF_SJ_BH: str = "Sjælland og Bonholm"
CONF_FYN: str = "Fyn"
CONF_JYL: str = "Jylland"
