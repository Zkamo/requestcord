from requestcord import *
logger = Logger("INF")

class ProfileEditor:
    USER_ENDPOINT = "https://discord.com/api/v9/users/@me"
    PROFILE_ENDPOINT = "https://discord.com/api/v9/users/@me/profile"

    @classmethod
    def change_avatar(cls, token: str, link: str) -> bool:
        """Update user's avatar from image URL"""
        try:
            response = requests.get(link, timeout=15)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                logger.error("Invalid image format: URL does not point to an image")
                return False
                
            image_type = content_type.split('/')[-1]
            if image_type not in ['png', 'jpeg', 'jpg', 'gif', 'webp']:
                logger.error(f"Unsupported image format: {image_type}")
                return False
                
            image_data = response.content
            base64_avatar = base64.b64encode(image_data).decode('utf-8')
            
            encoded_avatar = f"data:{content_type};base64,{base64_avatar}"
            
            return cls._update_profile_field(
                token,
                {"avatar": encoded_avatar},
                "Avatar",
                endpoint=cls.USER_ENDPOINT
            )
            
        except RequestsError as e:
            logger.error(f"Failed to download avatar image: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Avatar update failed: {str(e)}")
            return False
        
    @classmethod
    def change_display(cls, token: str, name: str) -> bool:
        """Update user's display name"""
        return cls._update_profile_field(
            token, 
            {"global_name": name},
            "Display name",
            endpoint=cls.USER_ENDPOINT
        )

    @classmethod
    def change_pronouns(cls, token: str, pronouns: str) -> bool:
        """Update user's pronouns"""
        return cls._update_profile_field(
            token,
            {"pronouns": pronouns},
            "Pronouns"
        )

    @classmethod
    def change_about_me(cls, token: str, about_me: str) -> bool:
        """Update user's 'About Me' section"""
        return cls._update_profile_field(
            token,
            {"bio": about_me},
            "About me"
        )

    @classmethod
    def change_status(cls, token: str, status_type: str, custom_text: str, emoji: dict = None) -> bool:
        """
        Update user's status and custom status using Discord's settings protobuf.
        Valid status types: 'online', 'idle', 'dnd', 'invisible'.
        Emoji format (optional): {'name': '🚀', 'id': None} or {'name': 'custom_emoji', 'id': '1234567890'}.
        """
        try:
            valid_statuses = ['online', 'idle', 'dnd', 'invisible']
            if status_type not in valid_statuses:
                logger.error(f"Invalid status type: {status_type}")
                return False

            settings = PreloadedUserSettings()
            settings.status.status.value = status_type
            
            settings.status.custom_status.text = custom_text
            if emoji:
                settings.status.custom_status.emoji_name = emoji.get('name', '')
                eid = emoji.get('id')
                settings.status.custom_status.emoji_id = int(eid) if eid is not None else 0
            settings.status.custom_status.expires_at_ms = 0

            proto_bytes = settings.SerializeToString()
            encoded_settings = base64.b64encode(proto_bytes).decode("utf-8")

            reversed_settings = PreloadedUserSettings.FromString(base64.b64decode(encoded_settings))
            logger.debug("Reversed settings: " + str(reversed_settings))

            header_generator = HeaderGenerator()
            headers = header_generator.generate_headers(token)
            session = requests.Session(impersonate=header_generator.impersonate_target)

            response = session.patch(
                "https://discord.com/api/v9/users/@me/settings-proto/1",
                json={"settings": encoded_settings},
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                logger.success("Status updated successfully")
                return True

            logger.error(f"Status update failed (HTTP {response.status_code}): {response.text}")
            return False

        except RequestsError as e:
            logger.error(f"Status update network error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during status update: {str(e)}")
            return False
        
    @classmethod
    def _update_profile_field(cls, token: str, payload: dict, field_name: str, endpoint: str = None) -> bool:
        """Universal update method with header generation"""
        try:
            header_generator = HeaderGenerator()
            headers = header_generator.generate_headers(token)
            session = requests.Session(impersonate=header_generator.impersonate_target)

            target_endpoint = endpoint or cls.PROFILE_ENDPOINT

            response = session.patch(
                target_endpoint,
                json=payload,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                logger.success(f"{field_name} updated successfully")
                return True

            logger.error(f"{field_name} update failed (HTTP {response.status_code}): {response.text}")
            return False

        except RequestsError as e:
            logger.error(f"{field_name} update network error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during {field_name.lower()} update: {str(e)}")
            return False

class ServerEditor:
    @classmethod
    def change_avatar(cls, token: str, guild_id: str, link: str) -> bool:
        """
        Update the token's per-server avatar in a specific guild.
        Requires Discord Nitro.
        """
        try:
            response = requests.get(link, timeout=15)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                logger.error("Invalid image format: URL does not point to an image")
                return False
                
            image_type = content_type.split('/')[-1]
            if image_type not in ['png', 'jpeg', 'jpg', 'gif', 'webp']:
                logger.error(f"Unsupported image format: {image_type}")
                return False
                
            image_data = response.content
            base64_avatar = base64.b64encode(image_data).decode('utf-8')
            encoded_avatar = f"data:{content_type};base64,{base64_avatar}"
            
            endpoint = f"https://discord.com/api/v9/guilds/{guild_id}/members/@me"
            payload = {"avatar": encoded_avatar}
            
            return cls._update_guild_field(
                token,
                endpoint,
                payload,
                "Per-server avatar"
            )
            
        except RequestsError as e:
            logger.error(f"Failed to download server avatar image: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Per-server avatar update failed: {str(e)}")
            return False

    @classmethod
    def change_nick(cls, token: str, guild_id: str, nick: str) -> bool:
        """Update user's nickname in a specific server"""
        endpoint = f"https://discord.com/api/v9/guilds/{guild_id}/members/@me"
        return cls._update_guild_field(
            token,
            endpoint,
            {"nick": nick},
            "Server nickname"
        )

    @classmethod
    def _update_guild_field(cls, token: str, endpoint: str, payload: dict, field_name: str) -> bool:
        """Universal method to update guild-related fields"""
        try:
            header_generator = HeaderGenerator()
            headers = header_generator.generate_headers(token)
            session = requests.Session(impersonate=header_generator.impersonate_target)
    
            response = session.patch(
                endpoint,
                json=payload,
                headers=headers,
                timeout=15
            )
    
            if response.status_code == 200:
                logger.success(f"{field_name} updated successfully")
                return True
        
            error_data = response.json()
            if response.status_code == 403:
                if error_data.get('code') == 50013:
                    logger.error(f"Permission denied for {field_name} update: Missing 'Change Nickname' permission")
                    return False
                
            if response.status_code == 400:
                if "NITRO" in error_data.get('message', '').upper():
                    logger.error(f"Server avatar update failed: Discord Nitro subscription required")
                    return False
                if "MEMBER_PERMISSIONS" in error_data.get('message', '').upper():
                    logger.error(f"Permission denied: You don't have permission to modify this in the server")
                    return False

    
            logger.error(f"{field_name} update failed (HTTP {response.status_code}): {response.text}")
            return False
    
        except RequestsError as e:
            logger.error(f"{field_name} update network error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during {field_name.lower()} update: {str(e)}")
            return False