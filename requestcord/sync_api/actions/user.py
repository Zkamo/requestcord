from __future__ import annotations

from base64 import b64encode

from discord_protos import PreloadedUserSettings

from ..http import HTTPClient
from ...common.response import APIResponse
from ...common.utils import DiscordUtils, DiscordFileEncoder
from ...common.types import (
    GetUserPayload,
    EditAvatarPayload,
    EditUsernamePayload,
    EditBioPayload,
    EditClanTagPayload,
    ChangeLanguagePayload,
    ChangeAppearancePayload,
    ChangePasswordPayload,
    EditGlobalNamePayload,
    ChangeStatusPayload
)

class UserActions:
    """
    User-related Discord actions.
    """

    def __init__(self, http: HTTPClient):
        self._http = http

    def get(self, payload: GetUserPayload) -> APIResponse:
        """
        Get current user information.
        """
        path = (
            f"/users/@me"
        )

        return self._http.get(
            path=path,
            token=payload.token
            )
        
    def edit_avatar(self, payload: EditAvatarPayload) -> APIResponse:
        """
        Edit the user's avatar using a local file path or image URL
        """
        path = "/users/@me"
    
        DiscordUtils.fetch_session_id(token=payload.token)
    
        encoded = DiscordFileEncoder.encode(payload.avatar)
        if not encoded.success:
            return encoded
    
        json_data = {
            "avatar": encoded.data
        }
    
        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data
        )
        
    def edit_username(self, payload: EditUsernamePayload) -> APIResponse:
        """
        Edit the user's username.
        """
        path = (
            f"/users/@me"
        )
        
        json_data = {
            "username": payload.username,
            "password": payload.password
        }

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )
    
    def edit_global_name(self, payload: EditGlobalNamePayload) -> APIResponse:
        """
        Edit the user's global name.
        """
        path = (
            f"/users/@me"
        )

        json_data = {
            "global_name": payload.global_name
        }

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )
    
    def edit_bio(self, payload: EditBioPayload) -> APIResponse:
        """
        Edit the user's bio.
        """
        path = (
            f"/users/@me"
        )

        json_data = {
            "bio": payload.bio
        }

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )
    
    def change_status(self, payload: ChangeStatusPayload) -> APIResponse:
        """
        Changes the user's status.
        """
        path = (
            "/users/@me/settings-proto/1"
        )
        
        valid_statuses = ['online', 'idle', 'dnd', 'invisible']
        if payload.status_type not in valid_statuses:
            payload.status_type = "dnd"
            
        settings = PreloadedUserSettings()
        settings.status.status.value = payload.status_type
        settings.status.custom_status.text = payload.custom_text
        settings.status.custom_status.expires_at_ms = 0
        proto_bytes = settings.SerializeToString()
        encoded_settings = b64encode(proto_bytes).decode("utf-8")
        
        

        json_data = {
            "settings": encoded_settings,
        }
        
        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data
        )
    
        
    def edit_clan_tag(self, payload: EditClanTagPayload) -> APIResponse:  
        """
        Edit the user's clan tag settings.
        """
        path = (
            f"/users/@me/clan"
        )

        json_data = {
            "identity_guild_id": payload.identity_guild_id,
            "identity_enabled": payload.identity_enabled
        }

        return self._http.put(
            path=path,
            token=payload.token,
            json=json_data,
        )

    def change_language(self, payload: ChangeLanguagePayload) -> APIResponse:
        """
        Change the user's language.
        """
        path = (
            f"/users/@me/settings"
        )

        json_data = {
            "locale": payload.locale
        }

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )

    def change_appearance(self, payload: ChangeAppearancePayload) -> APIResponse:
        """
        Change the user's appearance (theme).
        """
        path = (
            f"/users/@me/settings"
        )

        json_data = {
            "theme": payload.theme
        }

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )
    
    def change_password(self, payload: ChangePasswordPayload) -> APIResponse:
        """
        Change the user's password.
        """
        path = (
            f"/users/@me"
        )

        json_data = {
            "password": payload.old_password,
            "new_password": payload.new_password
        }

        return self._http.patch(
            path=path,
            token=payload.token,
            json=json_data,
        )