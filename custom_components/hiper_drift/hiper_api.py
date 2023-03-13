""" ------------------------------------------------------------------
# File name : hiper_api.py
# Copyright 2023 KGN Data. All rights reserved.
# ------------------------------------------------------------------"""

import asyncio
from dataclasses import dataclass
import re

from aiohttp.client import ClientSession
import async_timeout
from bs4 import BeautifulSoup  # type: ignore

from .const import CONF_FYN, CONF_JYL, CONF_SJ_BH


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class HiperApi:
    """Hiper web interface"""

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

    # ------------------------------------------------------------------
    async def update(self) -> None:
        """Hiper web interface"""

        if self.session is None:
            self.session = ClientSession()
            self.close_session = True

        self.msg = await self._check_hiper(self.region)

        if self.session and self.close_session:
            await self.session.close()

    # ------------------------------------------------------
    async def _check_hiper(self, region: str) -> str:
        msg: str = ""
        self.is_on = False

        if region == CONF_SJ_BH:
            url: str = "https://www.hiper.dk/drift/region/sjaelland-og-bornholm"
        elif region == CONF_FYN:
            url = "https://www.hiper.dk/drift/region/fyn"
        elif region == CONF_JYL:
            url = "https://www.hiper.dk/drift/region/jylland"

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request("GET", url)  # type: ignore
                soup = BeautifulSoup(await response.text(), "html.parser")

            if (
                self.general_msg
                and soup.find(
                    string=re.compile("Ingen Generelle driftssager", re.IGNORECASE)
                )
                is None
            ):
                self.is_on = True
                msg = 'Generelle driftsager"'

            if (
                self.city_check
                and soup.find(
                    string=re.compile(" " + self.city.strip() + " ", re.IGNORECASE)
                )
                is not None
            ):
                self.is_on = True
                msg = "Lokale driftssager for " + self.city.strip()

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
                msg = (
                    "Lokale driftssager for " + self.city.strip() + " på " + self.street
                )

        except asyncio.TimeoutError:
            pass
        return msg
