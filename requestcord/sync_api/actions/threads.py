from __future__ import annotations

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.types import (
    CreateThreadPayload,
    DeleteThreadPayload
)

class ThreadActions:
    """
    Thread-related Discord actions.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def create(self, payload: CreateThreadPayload) -> APIResponse:
        """
        Create a new thread in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/threads"
        )

        json_data = {
            "name": payload.name,
            "auto_archive_duration": payload.auto_archive_duration,
            "type": payload.type,
            "invitable": payload.invitable,
        }

        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
        )
    
    def delete(self, payload: DeleteThreadPayload) -> APIResponse:
        """
        Delete a thread.
        """
        path = (
            f"/channels/{payload.thread_id}"
        )

        return self._http.delete(
            path=path,
            token=payload.token,
        )
    