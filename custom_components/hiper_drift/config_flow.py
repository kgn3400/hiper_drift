"""Config flow for Hiperdrift integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import voluptuous as vol

#  from homeassistant import config_entries
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaCommonFlowHandler,
    SchemaConfigFlowHandler,
    # SchemaFlowError,
    SchemaFlowFormStep,
)
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import (
    CONF_FYN_REGION_2,
    CONF_JYL_REGION_3,
    CONF_MATCH_CASE,
    CONF_MATCH_LIST,
    CONF_MATCH_WORD,
    CONF_REGION,
    CONF_SJ_BH_REGION_1,
    DOMAIN,
    DOMAIN_NAME,
    TRANSLATION_KEY_REGION,
)


# ------------------------------------------------------------------
async def _validate_input(
    handler: SchemaCommonFlowHandler, user_input: dict[str, Any]
) -> dict[str, Any]:
    """Validate the user input."""

    # if CONF_CITY not in user_input:
    #     user_input[CONF_CITY] = ""

    # if user_input[CONF_CITY_CHECK] and user_input[CONF_CITY].strip() == "":
    #     raise SchemaFlowError("missing_city")

    # if CONF_STREET not in user_input:
    #     user_input[CONF_STREET] = ""

    # if user_input[CONF_STREET_CHECK] and user_input[CONF_STREET].strip() == "":
    #     raise SchemaFlowError("missing_street")

    return user_input


CONFIG_OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REGION, default=CONF_SJ_BH_REGION_1): SelectSelector(
            SelectSelectorConfig(
                options=[CONF_SJ_BH_REGION_1, CONF_FYN_REGION_2, CONF_JYL_REGION_3],
                sort=True,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key=TRANSLATION_KEY_REGION,
            )
        ),
        vol.Optional(CONF_MATCH_LIST, default=[]): TextSelector(
            TextSelectorConfig(multiple=True)
        ),
        vol.Optional(CONF_MATCH_CASE, default=False): bool,
        vol.Optional(CONF_MATCH_WORD, default=False): bool,
    }
)

CONFIG_FLOW = {
    "user": SchemaFlowFormStep(
        CONFIG_OPTIONS_SCHEMA,
        validate_user_input=_validate_input,
    ),
}

OPTIONS_FLOW = {
    "init": SchemaFlowFormStep(
        CONFIG_OPTIONS_SCHEMA,
        validate_user_input=_validate_input,
    ),
}


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ConfigFlowHandler(SchemaConfigFlowHandler, domain=DOMAIN):
    """Handle a config or options flow."""

    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""

        return cast(str, DOMAIN_NAME)
