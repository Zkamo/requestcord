from __future__ import annotations

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.utils import DiscordFileEncoder, DiscordUtils
from ...common.types import (
    JoinGuildPayload,
    LeaveGuildPayload,
    GetGuildPayload,
    GetGuildChannelsPayload,
    GetGuildRolesPayload,
    GetGuildEmojisPayload,
    GetGuildInvitesPayload,
    CreateGuildPayload,
    DeleteGuildPayload,
)


class GuildActions:
    """
    Guild-related Discord actions.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def join(self, payload: JoinGuildPayload) -> APIResponse:
        """
        Join a guild via invite code.
        """
        path = f"/invites/{payload.invite_code}"
        
        resp = DiscordUtils.fetch_session_id(payload.token, fallback=True)
        session_id = resp.data["session_id"] if resp.data else None
            
        return self._http.post(
            path=path,
            token=payload.token,
            json={"session_id": session_id},
            context="Join Guild",
        )

    def leave(self, payload: LeaveGuildPayload) -> APIResponse:
        """
        Leave a guild by ID.
        """
        path = f"/users/@me/guilds/{payload.guild_id}"

        return self._http.delete(
            path=path,
            token=payload.token,
            json={},
            context="Leave Guild",
        )

    def create(self, payload: CreateGuildPayload) -> APIResponse:
        """
        Create a guild.
        """
        path = "/guilds"
    
        template_code = payload.guild_template_code or "2TffvPucqHkN"
    
        icon = payload.icon
        if icon and not icon.startswith("data:"):
            icon = DiscordFileEncoder.encode(icon)
    
        json_payload = {
            "name": payload.name,
            "icon": icon,
            "channels": payload.channels,
            "system_channel_id": payload.system_channel_id,
            "guild_template_code": template_code,
        }
    
        json_payload = {k: v for k, v in json_payload.items() if v is not None}
    
        return self._http.post(
            path=path,
            token=payload.token,
            json=json_payload,
        )

    def delete(self, payload: DeleteGuildPayload) -> APIResponse:
        """
        Delete a guild.
        """
        path = f"/guilds/{payload.guild_id}/delete"

        return self._http.post(
            path=path,
            token=payload.token,
            json={},
        )
        
    def get_guild(self, payload: GetGuildPayload) -> APIResponse:
        """
        Get guild information by ID.
        """
        path = f"/guilds/{payload.guild_id}"

        return self._http.get(
            path=path,
            token=payload.token,
        )
        
    def get_guild_channels(self, payload: GetGuildChannelsPayload) -> APIResponse:
        """
        Get guild channels by guild ID.
        """
        path = f"/guilds/{payload.guild_id}/channels"

        return self._http.get(
            path=path,
            token=payload.token,
        )
        
    def get_guild_roles(self, payload: GetGuildRolesPayload) -> APIResponse:
        """
        Get guild roles by guild ID.
        """
        path = f"/guilds/{payload.guild_id}/roles"

        return self._http.get(
            path=path,
            token=payload.token,
        )
        
    def get_guild_emojis(self, payload: GetGuildEmojisPayload) -> APIResponse:
        """
        Get guild emojis by guild ID.
        """
        path = f"/guilds/{payload.guild_id}/emojis"

        return self._http.get(
            path=path,
            token=payload.token,
        )
    
    def get_guild_invites(self, payload: GetGuildInvitesPayload) -> APIResponse:
        """
        Get guild invites by guild ID.
        """
        path = f"/guilds/{payload.guild_id}/invites"

        return self._http.get(
            path=path,
            token=payload.token,
        )