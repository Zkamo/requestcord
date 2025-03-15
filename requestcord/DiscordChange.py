from typing      import   Optional, Any, Dict, TypedDict
from functools   import   wraps
from random      import   uniform
from time        import   sleep
from base64      import   b64encode, b64decode

from curl_cffi   import   requests

from requestcord import   Snowflake, HeaderGenerator, Logger, PreloadedUserSettings, SessionID

class DiscordAPIResponse(TypedDict):
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
    status_code: int

class ProfileEditor:
    _API_BASE: str = "https://discord.com/api/v9"
    _MAX_RETRY_ATTEMPTS: int = 3

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._headers = HeaderGenerator()
        self.logger = logger or Logger(level='INF')
        self.session = SessionID()

    def _handle_rate_limits(func):
        """Handles rate-limitation from Discord."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(self._MAX_RETRY_ATTEMPTS + 1):
                result = func(self, *args, **kwargs)
                if result and result.get('error', {}).get('type') == 'RateLimitExceeded':
                    retry_after = result['error'].get('retry_after', 5)
                    jitter = uniform(0.5, 1.5)
                    sleep_time = retry_after * jitter
                    self.logger.info(
                        f"Rate limit hit - retrying in {sleep_time:.2f}s "
                        f"(Attempt {attempt+1}/{self._MAX_RETRY_ATTEMPTS})"
                    )
                    sleep(sleep_time)
                    continue
                return result
            return result
        return wrapper

    def _process_response(self, response: requests.Response) -> DiscordAPIResponse:
        """Uniform response processor for all API calls"""
        try:
            response_json = response.json() if response.content else {}
        except requests.JSONDecodeError:
            response_json = {}

        success = 200 <= response.status_code < 300
        result: DiscordAPIResponse = {
            'success': success,
            'data': response_json,
            'error': {} if success else None,
            'status_code': response.status_code
        }

        if not success:
            error_info = {
                400: ('BadRequest', 'Invalid request format'),
                401: ('AuthenticationError', 'Invalid credentials'),
                403: ('Forbidden', 'Missing permissions'),
                404: ('NotFound', 'Resource not found'),
                429: ('RateLimitExceeded', 'Too many requests')
            }.get(response.status_code, ('APIError', f'Request failed with status {response.status_code}'))
            result['error'] = {
                'type': error_info[0],
                'message': response_json.get('message', error_info[1]),
                'code': response_json.get('code'),
                'retry_after': response_json.get('retry_after')
            }

        return result

    @_handle_rate_limits
    def _update_profile_field(
        self,
        token: str,
        payload: Dict[str, Any],
        field_name: str,
        endpoint: Optional[str] = None,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        target_endpoint = endpoint or f"{self._API_BASE}/users/@me/profile"
        try:
            session = requests.Session(impersonate=self._headers.impersonate_target)
            response = session.patch(
                target_endpoint,
                json=payload,
                headers=self._headers.generate_headers(token),
                timeout=15,
                proxies=proxy or {}
            )
            if response.status_code == 200:
                self.logger.success(f"{field_name} updated successfully")
            else:
                self.logger.error(f"{field_name} update failed (HTTP {response.status_code}): {response.text}")
            return self._process_response(response)
        except Exception as e:
            self.logger.error(f"Unexpected error during {field_name.lower()} update: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def change_avatar(
        self,
        token: str,
        link: str,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        try:
            img_response = requests.get(link, timeout=15, proxies=proxy or {})
            img_response.raise_for_status()
            content_type = img_response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                self.logger.error("Invalid image format: URL does not point to an image")
                return {'success': False, 'data': None, 'error': {'type': 'InvalidImageFormat', 'message': 'URL does not point to an image'}, 'status_code': 0}
            image_type = content_type.split('/')[-1]
            if image_type not in ['png', 'jpeg', 'jpg', 'gif', 'webp']:
                self.logger.error(f"Unsupported image format: {image_type}")
                return {'success': False, 'data': None, 'error': {'type': 'UnsupportedImageFormat', 'message': f"Unsupported image format: {image_type}"}, 'status_code': 0}
            image_data = img_response.content
            base64_avatar = b64encode(image_data).decode('utf-8')
            encoded_avatar = f"data:{content_type};base64,{base64_avatar}"
            opensession = self.session.get_session(token=token)
            return self._update_profile_field(token, {"avatar": encoded_avatar}, "Avatar", endpoint=f"{self._API_BASE}/users/@me", proxy=proxy)
        except Exception as e:
            self.logger.error(f"Avatar update failed: {str(e)}")
            return {'success': False, 'data': None, 'error': {'type': 'ConnectionError', 'message': str(e)}, 'status_code': 0}
    
    @_handle_rate_limits
    def change_display(self, token: str, name: str, proxy: Optional[Dict[str, str]] = None) -> DiscordAPIResponse:
        opensession = self.session.get_session(token=token)
        return self._update_profile_field(token, {"global_name": name}, "Display name", endpoint=f"{self._API_BASE}/users/@me", proxy=proxy)
    
    @_handle_rate_limits
    def change_pronouns(self, token: str, pronouns: str, proxy: Optional[Dict[str, str]] = None) -> DiscordAPIResponse:
        return self._update_profile_field(token, {"pronouns": pronouns}, "Pronouns", endpoint=f"{self._API_BASE}/users/@me", proxy=proxy)
    
    @_handle_rate_limits
    def change_about_me(self, token: str, about_me: str, proxy: Optional[Dict[str, str]] = None) -> DiscordAPIResponse:
        return self._update_profile_field(token, {"bio": about_me}, "About me", endpoint=f"{self._API_BASE}/users/@me", proxy=proxy)

    @_handle_rate_limits
    def change_status(
        self,
        token: str,
        status_type: str,
        custom_text: str,
        emoji: Optional[Dict[str, Any]] = None,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        try:
            valid_statuses = ['online', 'idle', 'dnd', 'invisible']
            if status_type not in valid_statuses:
                self.logger.error(f"Invalid status type: {status_type}")
                return {'success': False, 'data': None, 'error': {'type': 'ValidationError', 'message': f"Invalid status type: {status_type}"}, 'status_code': 0}
            settings = PreloadedUserSettings()
            settings.status.status.value = status_type
            settings.status.custom_status.text = custom_text
            if emoji:
                settings.status.custom_status.emoji_name = emoji.get('name', '')
                eid = emoji.get('id')
                settings.status.custom_status.emoji_id = int(eid) if eid is not None else 0
            settings.status.custom_status.expires_at_ms = 0
            proto_bytes = settings.SerializeToString()
            encoded_settings = b64encode(proto_bytes).decode("utf-8")
            reversed_settings = PreloadedUserSettings.FromString(b64decode(encoded_settings))
            self.logger.debug("Reversed settings: " + str(reversed_settings))
            header_generator = self._headers
            headers = header_generator.generate_headers(token)
            session = requests.Session(impersonate=header_generator.impersonate_target)
            response = session.patch(
                f"{self._API_BASE}/users/@me/settings-proto/1",
                json={"settings": encoded_settings},
                headers=headers,
                timeout=15,
                proxies=proxy or {}
            )
            if response.status_code == 200:
                self.logger.success("Status updated successfully")
            else:
                self.logger.error(f"Status update failed (HTTP {response.status_code}): {response.text}")
            return self._process_response(response)
        except Exception as e:
            self.logger.error(f"Unexpected error during status update: {str(e)}")
            return {'success': False, 'data': None, 'error': {'type': 'ConnectionError', 'message': str(e)}, 'status_code': 0}

class ServerEditor:
    _API_BASE: str = "https://discord.com/api/v9"
    _MAX_RETRY_ATTEMPTS: int = 3

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._headers = HeaderGenerator()
        self.logger = logger or Logger(level='INF')
        self.session = SessionID()

    def _handle_rate_limits(func):
        """Handles rate-limitation from Discord."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(self._MAX_RETRY_ATTEMPTS + 1):
                result = func(self, *args, **kwargs)
                if result and result.get('error', {}).get('type') == 'RateLimitExceeded':
                    retry_after = result['error'].get('retry_after', 5)
                    jitter = uniform(0.5, 1.5)
                    sleep_time = retry_after * jitter
                    self.logger.info(
                        f"Rate limit hit - retrying in {sleep_time:.2f}s "
                        f"(Attempt {attempt+1}/{self._MAX_RETRY_ATTEMPTS})"
                    )
                    sleep(sleep_time)
                    continue
                return result
            return result
        return wrapper

    def _process_response(self, response: requests.Response) -> DiscordAPIResponse:
        """Uniform response processor for all API calls"""
        try:
            response_json = response.json() if response.content else {}
        except requests.JSONDecodeError:
            response_json = {}

        success = 200 <= response.status_code < 300
        result: DiscordAPIResponse = {
            'success': success,
            'data': response_json,
            'error': {} if success else None,
            'status_code': response.status_code
        }

        if not success:
            error_info = {
                400: ('BadRequest', 'Invalid request format'),
                401: ('AuthenticationError', 'Invalid credentials'),
                403: ('Forbidden', 'Missing permissions'),
                404: ('NotFound', 'Resource not found'),
                429: ('RateLimitExceeded', 'Too many requests')
            }.get(response.status_code, ('APIError', f'Request failed with status {response.status_code}'))
            result['error'] = {
                'type': error_info[0],
                'message': response_json.get('message', error_info[1]),
                'code': response_json.get('code'),
                'retry_after': response_json.get('retry_after')
            }

        return result

    @_handle_rate_limits
    def _update_guild_field(
        self,
        token: str,
        endpoint: str,
        payload: Dict[str, Any],
        field_name: str,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        try:
            session = requests.Session(impersonate=self._headers.impersonate_target)
            response = session.patch(
                endpoint,
                json=payload,
                headers=self._headers.generate_headers(token),
                timeout=15,
                proxies=proxy or {}
            )
            if response.status_code == 200:
                self.logger.success(f"{field_name} updated successfully")
            else:
                self.logger.error(f"{field_name} update failed (HTTP {response.status_code}): {response.text}")
            return self._process_response(response)
        except Exception as e:
            self.logger.error(f"Unexpected error during {field_name.lower()} update: {str(e)}")
            return {'success': False, 'data': None, 'error': {'type': 'ConnectionError', 'message': str(e)}, 'status_code': 0}

    @_handle_rate_limits
    def change_avatar(
        self,
        token: str,
        guild_id: Snowflake,
        link: str,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        try:
            img_response = requests.get(link, timeout=15, proxies=proxy or {})
            img_response.raise_for_status()
            content_type = img_response.headers.get('Content-Type', '')
            if not content_type.startswith('image/'):
                self.logger.error("Invalid image format: URL does not point to an image")
                return {'success': False, 'data': None, 'error': {'type': 'InvalidImageFormat', 'message': 'URL does not point to an image'}, 'status_code': 0}
            image_type = content_type.split('/')[-1]
            if image_type not in ['png', 'jpeg', 'jpg', 'gif', 'webp']:
                self.logger.error(f"Unsupported image format: {image_type}")
                return {'success': False, 'data': None, 'error': {'type': 'UnsupportedImageFormat', 'message': f"Unsupported image format: {image_type}"}, 'status_code': 0}
            image_data = img_response.content
            base64_avatar = b64encode(image_data).decode('utf-8')
            encoded_avatar = f"data:{content_type};base64,{base64_avatar}"
            endpoint = f"{self._API_BASE}/guilds/{guild_id}/members/@me"
            payload = {"avatar": encoded_avatar}
            opensession = self.session.get_session(token=token)
            return self._update_guild_field(token, endpoint, payload, "Per-server avatar", proxy=proxy)
        except Exception as e:
            self.logger.error(f"Per-server avatar update failed: {str(e)}")
            return {'success': False, 'data': None, 'error': {'type': 'ConnectionError', 'message': str(e)}, 'status_code': 0}

    def change_nick(
        self,
        token: str,
        guild_id: Snowflake,
        nick: str,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        endpoint = f"{self._API_BASE}/guilds/{guild_id}/members/@me"
        opensession = self.session.get_session(token=token)
        return self._update_guild_field(token, endpoint, {"nick": nick}, "Server nickname", proxy=proxy)
