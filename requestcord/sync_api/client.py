from __future__ import annotations

from typing import Literal, Optional

from .http import HTTPClient
from .actions.guilds import GuildActions
from .actions.reactions import ReactionActions
from .actions.messages import MessageActions
from .actions.boosts import BoostActions
from .actions.members import MemberActions
from .actions.user import UserActions
from .actions.threads import ThreadActions
from .actions.forum import ForumActions

HTTPBackend = Literal["curl_cffi"]


class SyncClient:
    """
    Public entry point for the sync Requestcord API.
    """

    def __init__(
        self,
        *,
        backend: HTTPBackend = "curl_cffi",
        proxy: Optional[str] = None,
        timeout: int = 30,
        user_agent: Optional[str] = None,
        debug: bool = False,
    ):
        self.backend = backend
        self.proxy = proxy
        self.timeout = timeout
        self.user_agent = user_agent
        self.debug = debug

        self.http = HTTPClient(
            backend=backend,
            proxy=proxy,
            timeout=timeout,
            debug=debug,
        )

        self.guilds = GuildActions(self.http)
        self.reactions = ReactionActions(self.http)
        self.messages = MessageActions(self.http)
        self.boosts = BoostActions(self.http)
        self.members = MemberActions(self.http)
        self.user = UserActions(self.http)
        self.threads = ThreadActions(self.http)
        self.forum = ForumActions(self.http)
        
        self.raw = self.http

    def close(self) -> None:
        """Close underlying HTTP session(s)."""
        self.http.close()

    def __enter__(self) -> SyncClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
