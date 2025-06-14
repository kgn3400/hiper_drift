"""Component api for Hiper drift."""

from asyncio import timeout
from dataclasses import dataclass
from datetime import timedelta
from re import IGNORECASE, Pattern, compile, escape
from typing import Any

from aiohttp.client import ClientSession

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_MATCH_CASE,
    CONF_MATCH_LIST,
    CONF_MATCH_WORD,
    CONF_READ_GLOBAL,
    CONF_READ_REGIONAL,
    CONF_REGION,
    CONF_UPDATED_AT_GLOBAL,
    CONF_UPDATED_AT_REGIONAL,
    DOMAIN,
    LOGGER,
    IssueType,
)
from .hass_util import (
    DictToObject,
    JsonExt,
    handle_retries,
    set_supress_config_update_listener,
)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class MessageItem:
    """message item."""

    def __init__(self) -> None:
        """Init."""
        self.created_at: str | None = ""
        self.message: str | None = ""


# ------------------------------------------------------------------
# ------------------------------------------------------------------
@dataclass
class IssueItem:
    """Issue item."""

    def __init__(self) -> None:
        """Init."""
        self.subject: str | None = ""
        self.created_dtm: str | None = ""
        self.area: str | None = ""
        self.eta: str | None = ""
        self.region: str | None = ""
        self.region_id: int | None = 0
        self.is_unfolded: bool | None = False
        self.is_pinned: bool | None = False
        self.updated_at: str | None = ""
        self.finished_at: str | None = ""
        self.status: str | None = ""
        self.messages: list[MessageItem] | None = []

        self.text: str | None = ""
        self.markdown: str | None = ""


class HiperIssues(JsonExt, DictToObject):
    """Hiper issues."""

    def __init__(self, tmp_json: str | None = None) -> None:
        """Init."""
        self.globals: list[IssueItem] = []
        self.regionals: list[IssueItem] = []
        self.finisheds: list[IssueItem] = []
        super().__init__()

        if tmp_json is None:
            return

        self.reload(tmp_json)

    def reload(self, tmp_json: str) -> None:
        """Reload."""
        try:
            self.dict_to_object(
                self.json_str_to_dict(
                    tmp_json,
                    {
                        "global": "globals",
                        "regional": "regionals",
                        "finished": "finisheds",
                    },
                )
            )
        except Exception as exp:  # noqa: BLE001
            LOGGER.error("Error reloading Hiper issues: %s", exp)


# ------------------------------------------------------------------
# ------------------------------------------------------------------
class ComponentApi:
    """Hiper interface."""

    ISSUES_URL: str = "https://drift-api.hiper.dk/issues"

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
        session: ClientSession | None,
    ) -> None:
        """Hiper api."""

        self.hass: HomeAssistant = hass
        self.coordinator: DataUpdateCoordinator = coordinator
        self.entry: ConfigEntry = entry
        self.session: ClientSession | None = session

        self.issues: HiperIssues = HiperIssues()
        self.issue_general: IssueItem | None = None
        self.issue_regional: IssueItem | None = None

        self.region: str = entry.options[CONF_REGION]

        self.updated_at_regional: str = entry.options.get(CONF_UPDATED_AT_REGIONAL, "")
        self.read_regional: bool = entry.options.get(CONF_READ_REGIONAL, False)
        self.updated_at_global: str = entry.options.get(CONF_UPDATED_AT_GLOBAL, "")
        self.read_global: bool = entry.options.get(CONF_READ_GLOBAL, False)

        self.request_timeout: int = 5
        self.close_session: bool = False

        self.coordinator.update_interval = timedelta(minutes=15)
        self.coordinator.update_method = self.async_update

        """Setup the actions for the Hiper integration."""
        hass.services.async_register(DOMAIN, "update", self.async_update_service)
        hass.services.async_register(
            DOMAIN, "markasread", self.async_mark_as_read_service
        )

        self.regex_comp: Pattern | None = self.compile_all_words_regex(
            entry.options.get(CONF_MATCH_LIST),
            entry.options.get(CONF_MATCH_WORD, False),
            entry.options.get(CONF_MATCH_CASE, False),
        )

    # ------------------------------------------------------------------
    def compile_all_words_regex(
        self,
        words: list[str],
        use_word_boundaries: bool = True,
        case_sensitive: bool = False,
    ) -> Pattern[str] | None:
        r"""Return a compiled regex pattern that matches if ALL words in the list are present in a text.

        - words: A list of words to match.
        - use_word_boundaries: If True, only matches whole words.
        - case_sensitive: If False, matches regardless of letter case.
        regex : ^(?=.*\btest\b)(?=.*\bregex\b)(?=.*\bstrenge\b).*

        """

        if len(words) == 0:
            return None

        lookaheads: list[str] = []

        for word in words:
            if word.strip() != "":
                if use_word_boundaries:
                    pattern = rf"(?=.*\b{escape(word)}\b)"
                else:
                    pattern = rf"(?=.*{escape(word)})"
                lookaheads.append(pattern)
        combined_pattern: str = "^" + "".join(lookaheads) + ".*"
        flags: int = 0 if case_sensitive else IGNORECASE
        return compile(combined_pattern, flags)

    # ------------------------------------------------------------------
    async def async_mark_as_read_service(self, call: ServiceCall) -> None:
        """Hiper service interface."""
        self.read_global = True
        self.read_regional = True

        await self.async_update_config()
        await self.coordinator.request_refresh()

    # ------------------------------------------------------------------
    async def async_update_service(self, call: ServiceCall) -> None:
        """Hiper service interface."""
        self.updated_at_global = ""
        self.read_global = False
        self.updated_at_regional = ""
        self.read_regional = False

        await self.async_update_config()

        await self.async_update()
        await self.coordinator.request_refresh()

    # ------------------------------------------------------------------
    async def async_update(self) -> None:
        """Hiper interface."""

        if self.session is None:
            self.session = ClientSession()
            self.close_session = True

        await self.async_check_hiper(self.region)

        if self.session and self.close_session:
            await self.session.close()

    # ------------------------------------------------------
    @handle_retries(retries=5, retry_delay=5)
    async def _async_get_issues(self) -> str:
        async with timeout(self.request_timeout):
            response = await self.session.get(self.ISSUES_URL)

        return await response.text()

    # ------------------------------------------------------
    async def async_create_issue_text(
        self, issue: IssueItem, issue_type: IssueType
    ) -> str:
        """Create issue text."""

        return (
            issue.subject
            + "\n"
            + issue.area
            + "\n"
            + "Forventet færdig: "
            + issue.eta
            + "\n"
            + "Opdateret: "
            + issue.updated_at
            + "\n"
        )

    # ------------------------------------------------------
    async def async_create_issue_markdownt(
        self, issue: IssueItem, issue_type: IssueType
    ) -> str:
        """Create issue markdown."""

        return (
            '### <font color=red> <ha-icon icon="mdi:router-network"></ha-icon></font> '
            + (
                "  Hiper - Generelle Driftssager"
                if issue_type == IssueType.GENEREL
                else "  Hiper - Regionale driftssager"
            )
            + "\n"
            + issue.subject
            + "\n\n"
            + issue.area
            + "\n\n"
            + ("Forventet færdig : " + issue.eta + "\n" if issue.eta else "")
            + "Opdateret : "
            + issue.updated_at
            + "\n"
        )

    # ------------------------------------------------------
    async def async_handle_general_issue(self, issue: IssueItem) -> None:
        """Handle general issue."""

        self.issue_general = issue
        self.issue_general.text = await self.async_create_issue_text(
            issue, IssueType.GENEREL
        )

        self.issue_general.markdown = await self.async_create_issue_markdownt(
            issue, IssueType.GENEREL
        )

    # ------------------------------------------------------
    async def async_handle_regional_issue(self, issue: IssueItem) -> None:
        """Handle regional issue."""

        self.issue_regional = issue
        self.issue_regional.text = await self.async_create_issue_text(
            issue, IssueType.REGIONAL
        )

        self.issue_regional.markdown = await self.async_create_issue_markdownt(
            issue, IssueType.REGIONAL
        )

    # ------------------------------------------------------
    async def async_check_hiper(self, region: str) -> None:
        """Check if Hiper drift."""

        self.issue_general = None
        self.issue_regional = None

        self.issues.reload(await self._async_get_issues())

        for item in self.issues.globals:
            if item.updated_at != self.updated_at_global:
                self.updated_at_global = item.updated_at
                self.read_global = False
                await self.async_update_config()

            if not self.read_global:
                await self.async_handle_general_issue(item)

            break

        region_num: int = int(region[-1])

        for item in self.issues.regionals:
            if item.region_id == region_num and (
                self.regex_comp is None
                or self.regex_comp.match(item.subject + item.area)
            ):
                if item.updated_at != self.updated_at_regional:
                    self.updated_at_regional = item.updated_at
                    self.read_regional = False
                    await self.async_update_config()

                if not self.read_regional:
                    await self.async_handle_regional_issue(item)

                break

    # ------------------------------------------------------------------
    @set_supress_config_update_listener()
    async def async_update_config(self) -> None:
        """Update config."""

        tmp_options: dict[str, Any] = self.entry.options.copy()

        tmp_options[CONF_UPDATED_AT_REGIONAL] = self.updated_at_regional
        tmp_options[CONF_READ_REGIONAL] = self.read_regional
        tmp_options[CONF_UPDATED_AT_GLOBAL] = self.updated_at_global
        tmp_options[CONF_READ_GLOBAL] = self.read_global

        self.hass.config_entries.async_update_entry(
            self.entry, data=tmp_options, options=tmp_options
        )
