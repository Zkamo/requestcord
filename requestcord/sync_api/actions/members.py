from __future__ import annotations

import datetime

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.types import (
    KickMemberPayload,
    BanMemberPayload,
    TimeoutMemberPayload,
    MuteMemberPayload,
    DeafenMemberPayload,
    ChangeNickMemberPayload,
)


class MemberActions:
    """
    Member-related actions within a guild.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def kick(self, payload: KickMemberPayload) -> APIResponse:
        path = (
            f"/guilds/{payload.guild_id}"
            f"/members/{payload.user_id}"
        )
        return self._http.delete(
            path=path,
            token=payload.token,
            json={"reason": payload.reason} if payload.reason else {},
        )

    def ban(self, payload: BanMemberPayload) -> APIResponse:
        path = (
            f"/guilds/{payload.guild_id}"
            f"/bans/{payload.user_id}"
        )
        json_payload = {
            "delete_message_days": payload.delete_message_days,
            "reason": payload.reason,
        }
        json_payload = {k: v for k, v in json_payload.items() if v is not None}
        return self._http.put(
            path=path,
            token=payload.token,
            json=json_payload,
        )

    def timeout(self, payload: TimeoutMemberPayload) -> APIResponse:
        path = (
            f"/guilds/{payload.guild_id}"
            f"/members/{payload.user_id}"
        )
        
        if payload.duration_seconds > 0:
            future_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=payload.duration_seconds)
            iso_timestamp = future_time.isoformat()
        else:
            iso_timestamp = None
        
        json_payload = {"communication_disabled_until": iso_timestamp}
        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_payload,
        )

    def mute(self, payload: MuteMemberPayload) -> APIResponse:
        path = (
            f"/guilds/{payload.guild_id}"
            f"/members/{payload.user_id}"
        )
        json_payload = {"mute": payload.mute}
        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_payload,
        )

    def deafen(self, payload: DeafenMemberPayload) -> APIResponse:
        path = (
            f"/guilds/{payload.guild_id}"
            f"/members/{payload.user_id}"
        )
        json_payload = {"deaf": payload.deafen}
        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_payload,
        )

    def change_nick(self, payload: ChangeNickMemberPayload) -> APIResponse:
        path = (
            f"/guilds/{payload.guild_id}"
            f"/members/{payload.user_id}"
        )
        json_payload = {"nick": payload.nick}
        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_payload,
        )