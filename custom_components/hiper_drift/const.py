"""Constants for Hiper driftsstatus DK integration."""

from enum import StrEnum
from logging import Logger, getLogger

DOMAIN = "hiper_drift"
DOMAIN_NAME = "Hiper drift"
LOGGER: Logger = getLogger(__name__)

CONF_MATCH_CASE = "match_case"
CONF_MATCH_WORD = "match_word"
CONF_MATCH_LIST = "match_list"

CONF_REGION = "region"
CONF_UPDATED_AT_REGIONAL = "updated_at_regional"
CONF_READ_REGIONAL = "read_regional"
CONF_IS_ON_REGIONAL = False
CONF_UPDATED_AT_GLOBAL = "updated_at_global"
CONF_READ_GLOBAL = "read_global"
CONF_IS_ON_GENERAL = False

TRANSLATION_KEY = DOMAIN
TRANSLATION_KEY_REGION = "region"
CONF_SJ_BH_REGION_1 = "sj_bh_1"
CONF_FYN_REGION_2 = "fyn_2"
CONF_JYL_REGION_3 = "jylland_3"


class IssueType(StrEnum):
    """Issue types."""

    GENEREL = "Generel"
    REGIONAL = "Regional"
