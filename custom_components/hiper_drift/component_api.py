"""Component api for Hiper drift."""

from asyncio import timeout
from dataclasses import dataclass
import re

from aiohttp.client import ClientSession
from bs4 import BeautifulSoup

from homeassistant.core import ServiceCall
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,  # type: ignore
)

from .const import CONF_FYN, CONF_SJ_BH  # CONF_JYL,


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
        """Hiper api.

        Args:
            session (ClientSession | None): _description_
            region (str): _description_
            general_msg (bool): _description_
            city_check (bool): _description_
            city (str): _description_
            street_check (bool): _description_
            street (str): _description_

        """

        self.session: ClientSession | None = session
        self.region: str = region
        self.general_msg: bool = general_msg
        self.city_check: bool = city_check
        self.city: str = city
        self.street_check: bool = street_check
        self.street: str = street
        self.request_timeout: int = 5
        self.close_session: bool = False
        self.is_on: bool = False
        self.msg: str = ""
        self.coordinator: DataUpdateCoordinator

    # ------------------------------------------------------------------
    async def async_update_service(self, call: ServiceCall) -> None:
        """Hiper service interface."""
        await self.async_update()
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    async def async_update(self) -> None:
        """Hiper interface."""

        if self.session is None:
            self.session = ClientSession()
            self.close_session = True

        self.msg = await self._async_check_hiper(self.region)

        if self.session and self.close_session:
            await self.session.close()

    # ------------------------------------------------------
    async def _async_check_hiper(self, region: str) -> str:
        msg: str = ""
        self.is_on = False

        if region == CONF_SJ_BH:
            url: str = "https://www.hiper.dk/drift/region/sjaelland-og-bornholm"
        elif region == CONF_FYN:
            url = "https://www.hiper.dk/drift/region/fyn"

        else:  # region == CONF_JYL:
            url = "https://www.hiper.dk/drift/region/jylland"

        try:
            async with timeout(self.request_timeout):
                response = await self.session.request("GET", url)  # type: ignore

                if response.real_url.path.upper().find("/region/".upper()) == -1:
                    return msg

                soup = BeautifulSoup(await response.text(), "html.parser")

            if (
                self.general_msg
                and soup.find(
                    string=re.compile("Ingen Generelle driftssager", re.IGNORECASE)
                )
                is None
            ):
                self.is_on = True
                msg = "Generelle driftsager"

            if (
                self.city_check
                and soup.find(
                    string=re.compile(" " + self.city.strip() + " ", re.IGNORECASE)
                )
                is not None
            ):
                self.is_on = True
                msg = "Lok" + "ale driftssager for " + self.city.strip()

            if (
                self.street_check
                and soup.find(
                    string=re.compile(" " + self.city.strip() + " ", re.IGNORECASE)
                )
                is not None
                and soup.find(
                    string=re.compile(" " + self.street.strip(), re.IGNORECASE)
                )
                is not None
            ):
                self.is_on = True
                msg = f"Lokale driftssager for {self.city.strip()} på {self.street}"

        except TimeoutError:
            pass
        return msg
