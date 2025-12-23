from __future__ import annotations

from ..http import HTTPClient
from ...common.utils import EmojiEncoder
from ...common.response import APIResponse
from ...common.types import (
    AddReactionPayload,
    AddSuperReactionPayload,
    RemoveReactionPayload,
    GetReactionUsersPayload,
    ClearReactionsPayload,
)


class ReactionActions:
    """
    Reaction-related Discord actions.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def add(self, payload: AddReactionPayload) -> APIResponse:
        """
        Add a reaction to a message.
        """
        path = (
            f"/channels/{payload.channel_id}"
            f"/messages/{payload.message_id}"
            f"/reactions/{EmojiEncoder.encode(payload.emoji)}/@me"
        )

        return self._http.put(
            path=path,
            token=payload.token,
        )

    def add_super(self, payload: AddSuperReactionPayload) -> APIResponse:
        """
        Add a SUPER reaction to a message.
        """
        path = (
            f"/channels/{payload.channel_id}"
            f"/messages/{payload.message_id}"
            f"/reactions/{EmojiEncoder.encode_super(payload.emoji)}/@me"
        )

        params = {
            'location': 'Message Reaction Picker',
            'type': '1'
        }
        return self._http.put(
            path=path,
            token=payload.token,
            params=params,
        )
    
    def remove(self, payload: RemoveReactionPayload) -> APIResponse:
        """
        Remove a reaction from a message.
        """
        user = payload.user_id or "@me"

        path = (
            f"/channels/{payload.channel_id}"
            f"/messages/{payload.message_id}"
            f"/reactions/{EmojiEncoder.encode(payload.emoji)}/{user}"
        )

        return self._http.delete(
            path=path,
            token=payload.token,
        )

    def get_users(self, payload: GetReactionUsersPayload) -> APIResponse:
        """
        Get users who reacted with a specific emoji.
        """
        params = {"limit": payload.limit}
        if payload.after:
            params["after"] = payload.after

        path = (
            f"/channels/{payload.channel_id}"
            f"/messages/{payload.message_id}"
            f"/reactions/{EmojiEncoder.encode(payload.emoji)}"
        )

        return self._http.get(
            path=path,
            token=payload.token,
            params=params,
        )

    def clear(self, payload: ClearReactionsPayload) -> APIResponse:
        """
        Clear reactions from a message.
        """
        if payload.emoji:
            path = (
                f"/channels/{payload.channel_id}"
                f"/messages/{payload.message_id}"
                f"/reactions/{EmojiEncoder.encode(payload.emoji)}"
            )
        else:
            path = (
                f"/channels/{payload.channel_id}"
                f"/messages/{payload.message_id}"
                f"/reactions"
            )

        return self._http.delete(
            path=path,
            token=payload.token,
        )
