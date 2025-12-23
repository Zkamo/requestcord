from __future__ import annotations

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.types import (
    GetBoostSlotsPayload,
    BoostGuildPayload,
    RemoveGuildBoostPayload
)

class BoostActions:
    """
    Boost-related Discord actions.
    """
    
    def __init__(self, http: HTTPClient):
        self._http = http
    
    def get_slots(self, payload: GetBoostSlotsPayload) -> APIResponse:
        """
        Get available boost slots for the user.
        """
        path = (
            f"/users/@me/premium/subscriptions"
        )

        return self._http.get(
            path=path,
            token=payload.token,
            json={},
        )
    
    def boost_guild(self, payload: BoostGuildPayload) -> APIResponse:
        """
        Boost a guild.
        """
        path = (
            f"/guilds/{payload.guild_id}/premium/subscriptions"
        )
        
        json_data = {
            "user_premium_guild_subscription_slot_ids": payload.subscription_slot_ids
        }
        
        return self._http.post(
            path=path,
            token=payload.token,
            json=json_data,
        )
        
    def remove_boost(self, payload: RemoveGuildBoostPayload) -> APIResponse:
        """
        Remove boosts from a guild.
        """
        path = (
            f"/guilds/{payload.guild_id}/premium/subscriptions"
        )
        
        json_data = {
            "user_premium_guild_subscription_slot_ids": payload.subscription_slot_ids
        }
        
        return self._http.delete(
            path=path,
            token=payload.token,
            json=json_data,
        )
        
        