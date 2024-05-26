"""Component api for Hiper drift."""

from asyncio import timeout
from dataclasses import dataclass
from datetime import UTC, datetime
import re

from aiohttp.client import ClientSession
from bs4 import BeautifulSoup

from homeassistant.core import ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_FYN_REGION, CONF_SJ_BH_REGION


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class ComponentApi:
    """Hiper interface."""

    def __init__(
        self,
        session: ClientSession | None,
        region: str,
        general_msg: bool,
        city_check: bool,
        city: str,
        street_check: bool,
        street: str,
    ) -> None:
        """Hiper api."""

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
        self.msg: str = ""
        self.content: str = ""
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
        # self.msg: str = ""
        # self.content = ""
        # self.is_on = False

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

                soup = BeautifulSoup(await response.text(), "html.parser")

            if (
                self.general_msg
                and (
                    xx := soup.find(
                        string=re.compile("Generelle driftssager", re.IGNORECASE)
                    )
                )
                is not None
                and not xx.strip().startswith("Ingen")
            ):
                tmp_msg = "Generelle driftsager"

                tag = soup.select(
                    "body > div.site-wrap > main > div.service-status-wrapper > section > div:nth-child(1) > ul > li > div > div.details"
                )[0]
                tmp_content = tag.text.strip()
                is_updated = True

            async with timeout(self.request_timeout):
                response = await self.session.request("GET", url_region)

                soup = BeautifulSoup(await response.text(), "html.parser")

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
                        f"Lokale driftssager for {self.city.strip()} på {self.street}"
                    )
                    tmp_content = xx.strip()
                    is_updated = True

            if is_updated:
                if tmp_msg != self.msg or tmp_content != self.content:
                    self.msg = tmp_msg
                    self.content = tmp_content
                    self.is_on = True
                    self.last_updated = datetime.now(UTC)
            else:
                self.msg = ""
                self.content = ""
                self.is_on = False
                self.last_updated = None

        except TimeoutError:
            pass
