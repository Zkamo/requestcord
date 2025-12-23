from __future__ import annotations

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.types import (
    CreateForumPayload,
    FollowPostPayload,
    UnfollowPostPayload,
)

class ForumActions:
    """
    Forum-related Discord actions.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def create(self, payload: CreateForumPayload) -> APIResponse:
        """
        Create a new forum thread in a channel.
        """
        path = (
            f"/channels/{payload.channel_id}/threads"
        )

        json_data = {
            "name": payload.name,
            "auto_archive_duration": payload.auto_archive_duration,
            "type": payload.type,
            "invitable": payload.invitable,
            "message": {"content": payload.content}
        }

        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
        )
    
    def follow_post(self, payload: FollowPostPayload) -> APIResponse:
        """
        Follow a forum post channel.
        """
        path = (
            f"/channels/{payload.post_id}/thread-members/@me"
        )

        return self._http.post(
            path=path,
            token=payload.token,
            json={},
        )
    
    def unfollow_post(self, payload: UnfollowPostPayload) -> APIResponse:
        """
        Unfollow a forum post channel.
        """
        path = (
            f"/channels/{payload.post_id}/thread-members/@me"
        )

        return self._http.delete(
            path=path,
            token=payload.token,
        )

