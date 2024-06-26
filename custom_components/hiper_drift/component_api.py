"""Component api for Hiper drift."""

from asyncio import timeout
from dataclasses import dataclass
from datetime import UTC, datetime
import re
from typing import Any

from aiohttp.client import ClientSession
from bs4 import BeautifulSoup

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_CONTENT, CONF_FYN_REGION, CONF_MSG, CONF_SJ_BH_REGION


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class ComponentApi:
    """Hiper interface."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        session: ClientSession | None,
        region: str,
        general_msg: bool,
        city_check: bool,
        city: str,
        street_check: bool,
        street: str,
    ) -> None:
        """Hiper api."""

        self.hass: HomeAssistant = hass
        self.entry: ConfigEntry = entry
        self.session: ClientSession | None = session
        self.region: str = region
        self.general_msg: bool = general_msg
        self.city_check: bool = city_check
        self.city: str = city
        self.street_check: bool = street_check
        self.street: str = street
        self.request_timeout: int = 10
        self.close_session: bool = False
        self.is_on: bool = False
        self.msg: str = self.entry.options.get(CONF_MSG, "")
        self.content: str = self.entry.options.get(CONF_CONTENT, "")
        self.coordinator: DataUpdateCoordinator
        self.last_updated: datetime = None

    # ------------------------------------------------------------------
    async def async_reset_service(self, call: ServiceCall) -> None:
        """Hiper service interface."""
        self.is_on = False
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    async def async_update_service(self, call: ServiceCall) -> None:
        """Hiper service interface."""
        self.msg = ""
        self.content = ""
        self.update_config("", "")

        await self.async_update()
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    async def async_update(self) -> None:
        """Hiper interface."""

        if self.session is None:
            self.session = ClientSession()
            self.close_session = True

        await self._async_check_hiper(self.region)

        if self.session and self.close_session:
            await self.session.close()

    # ------------------------------------------------------
    async def _async_check_hiper(self, region: str) -> None:
        tmp_msg: str = ""
        tmp_content: str = ""
        is_updated: bool = False

        if region == CONF_SJ_BH_REGION:
            url_region: str = "https://www.hiper.dk/drift/region/sjaelland-og-bornholm"
        elif region == CONF_FYN_REGION:
            url_region = "https://www.hiper.dk/drift/region/fyn"

        else:  # region == CONF_JYL_REGION:
            url_region = "https://www.hiper.dk/drift/region/jylland"

        try:
            async with timeout(self.request_timeout):
                response = await self.session.request(
                    "GET", "https://www.hiper.dk/drift"
                )

                soup = await self.hass.async_add_executor_job(
                    BeautifulSoup, await response.text(), "lxml"
                )

            if (
                self.general_msg
                and soup.find(string=re.compile("generelle driftssager", re.IGNORECASE))
                is not None
                and soup.find(
                    string=re.compile("ingen generelle driftssager", re.IGNORECASE)
                )
                is None
            ):
                tmp_msg = "Generelle driftsager"

                tag = soup.select(
                    "body > div.site-wrap > main > div.service-status-wrapper > section > div:nth-child(1) > ul > li > div > div.details"
                )[0]
                tmp_content = tag.text.strip()
                is_updated = True

            async with timeout(self.request_timeout):
                response = await self.session.request("GET", url_region)

                soup = await self.hass.async_add_executor_job(
                    BeautifulSoup, await response.text(), "lxml"
                )

            if response.real_url.path.upper().find("/region/".upper()) == -1:
                if (
                    self.city_check
                    and (
                        xx := soup.find(
                            string=re.compile(
                                " " + self.city.strip() + " ", re.IGNORECASE
                            )
                        )
                    )
                    is not None
                ):
                    tmp_msg = "Lok" + f"ale driftssager for {self.city.strip()}"
                    tmp_content = xx.strip()
                    is_updated = True

                if (
                    self.street_check
                    and soup.find(
                        string=re.compile(" " + self.city.strip() + " ", re.IGNORECASE)
                    )
                    is not None
                    and (
                        xx := soup.find(
                            string=re.compile(" " + self.street.strip(), re.IGNORECASE)
                        )
                    )
                    is not None
                ):
                    tmp_msg = (
                        "Lok"
                        f"ale driftssager for {self.city.strip()} på {self.street}"
                    )
                    tmp_content = xx.strip()
                    is_updated = True

            if is_updated:
                if tmp_msg != self.msg or tmp_content != self.content:
                    self.msg = tmp_msg
                    self.content = tmp_content
                    self.is_on = True
                    self.last_updated = datetime.now(UTC)
                    self.update_config(tmp_msg, tmp_content)
            else:
                if self.is_on:
                    self.update_config("", "")

                self.msg = ""
                self.content = ""
                self.is_on = False
                self.last_updated = None

        except TimeoutError:
            pass

    # ------------------------------------------------------------------
    def update_config(self, msg: str, content: str) -> None:
        """Update config."""

        tmp_options: dict[str, Any] = self.entry.options.copy()
        tmp_options[CONF_MSG] = msg
        tmp_options[CONF_CONTENT] = content

        self.hass.config_entries.async_update_entry(
            self.entry, data=tmp_options, options=tmp_options
        )
