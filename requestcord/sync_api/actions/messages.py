from __future__ import annotations

from typing import Dict, Any

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.types import (
    CreateMessagePayload,
    DeleteMessagePayload,
    EditMessagePayload,
    ReplyMessagePayload,
    CreatePollPayload,
    ForwardMessagePayload,
    PinMessagePayload,
    UnpinMessagePayload,
    TriggerTypingPayload,
)


class MessageActions:
    """
    Message-related Discord actions.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def create(self, payload: CreateMessagePayload) -> APIResponse:
        """
        Create a message in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/messages"
        )        

        json_data = {
            "content": payload.content,
            "tts": payload.tts,
        }

        if payload.nonce:
            json_data["nonce"] = payload.nonce

        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
        )

    def delete(self, payload: DeleteMessagePayload) -> APIResponse:
        """
        Delete a message in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/messages/{payload.message_id}"
        )
        
        return self._http.delete(
            path=path,
            token=payload.token,
            json={},
        )

    def edit(self, payload: EditMessagePayload) -> APIResponse:
        """
        Edit a message in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/messages/{payload.message_id}"
        )        

        json_data: Dict[str, Any] = {}
        if payload.content is not None:
            json_data["content"] = payload.content

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )

    def reply(self, payload: ReplyMessagePayload) -> APIResponse:
        """
        Reply to a message in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/messages"
        )        
        
        json_data: Dict[str, Any] = {
            "content": payload.content,
            "message_reference": {"message_id": payload.message_id},
        }
        
        if payload.mention_author:
            json_data["allowed_mentions"] = {"replied_user": True}
        else:
            json_data["allowed_mentions"] = {"replied_user": False}

        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
        )

    def create_poll(self, payload: CreatePollPayload) -> APIResponse:
        """
        Create a native Discord poll in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/messages"
        )        

        json_data: Dict[str, Any] = {
            "content": "",
            "tts": False,
            "flags": 0,
            "poll": {
                "question": {"text": payload.question},
                "answers": [
                    {"poll_media": {"text": answer}}
                    for answer in payload.answers
                ],
                "allow_multiselect": payload.allow_multiple,
                "duration": payload.duration_hours,
                "layout_type": 1,
            },
        }

        if getattr(payload, "nonce", None):
            json_data["nonce"] = payload.nonce

        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
            context="Create Poll",
        )

    def forward(self, payload: ForwardMessagePayload) -> APIResponse:
        """
        Forward a message from one channel to another using message_reference.
        """
        path = (
            f"/channels/{payload.to_channel_id}/messages"
        )

        json_data = {
            "content": "",
            "message_reference": {
                "guild_id": payload.guild_id,
                "channel_id": payload.from_channel_id,
                "message_id": payload.message_id,
                "type": 1,
            },
            "tts": False,
            "flags": 0,
        }

        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
        )

    def pin(self, payload: PinMessagePayload) -> APIResponse:
        """
        Pin a message in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/pins/{payload.message_id}"
        )
        
        return self._http.put(
            path=path,
            token=payload.token,
            json={},
        )

    def unpin(self, payload: UnpinMessagePayload) -> APIResponse:
        """
        Unpin a message in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/pins/{payload.message_id}"
        )

        return self._http.delete(
            path=path,
            token=payload.token,
            json={},
        )

    def trigger_typing(self, payload: TriggerTypingPayload) -> APIResponse:
        """
        Trigger typing indicator in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/typing"
        )

        return self._http.post(
            path=path,
            token=payload.token,
            json={},
        )
