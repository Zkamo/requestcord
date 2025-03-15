from typing      import   Optional, Any, Dict, TypedDict, List
from functools   import   wraps
from random      import   uniform
from time        import   sleep

from curl_cffi   import   requests

from requestcord import   Snowflake, HeaderGenerator, Logger

class DiscordAPIResponse(TypedDict):
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
    status_code: int

class APIRequests:
    _API_BASE: str = "https://discord.com/api/v9"
    _MAX_RETRY_ATTEMPTS: int = 3

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._headers = HeaderGenerator()
        self.logger = logger or Logger(level='INF')

    def _handle_rate_limits(func):
        """Handles Rate-Limitation from discord."""
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
            }.get(response.status_code, 
                ('APIError', f'Request failed with status {response.status_code}'))

            result['error'] = {
                'type': error_info[0],
                'message': response_json.get('message', error_info[1]),
                'code': response_json.get('code'),
                'retry_after': response_json.get('retry_after')
            }

        return result

    @_handle_rate_limits
    def create_message(
        self,
        token: str,
        channel_id: Snowflake,
        content: str,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Creates a message in a Discord channel.
        """
        if not 1 <= len(content) <= 2000:
            return {
                'success': False,
                'error': {'type': 'ValidationError', 'message': 'Invalid content length'},
                'status_code': 0
            }

        try:
            response = requests.post(
                f"{self._API_BASE}/channels/{channel_id}/messages",
                json={"content": content, **kwargs},
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def add_reaction(
        self,
        token: str,
        channel_id: Snowflake,
        message_id: Snowflake,
        emoji: str,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """
        Adds a reaction to a message.
        """
        try:
            response = requests.put(
                f"{self._API_BASE}/channels/{channel_id}/messages/{message_id}"
                f"/reactions/{emoji}/@me",
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def create_poll(
        self,
        token: str,
        channel_id: Snowflake,
        question: str,
        answers: List[Dict[str, Any]],
        duration_hours: int,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """Creates a native Discord poll"""
        payload = {
            "poll": {
                "question": {"text": question},
                "answers": answers,
                "duration": duration_hours,
                "layout_type": 1
            },
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self._API_BASE}/channels/{channel_id}/messages",
                json=payload,
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=kwargs.get('proxy')
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def delete_message(
        self,
        token: str,
        channel_id: Snowflake,
        message_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """Deletes a message in a channel"""
        try:
            response = requests.delete(
                f"{self._API_BASE}/channels/{channel_id}/messages/{message_id}",
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def check_token(
        self,
        token: str,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """Comprehensive token analysis with enhanced metadata"""
        try:
            user_resp = requests.get(
                f"{self._API_BASE}/users/@me",
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            result = self._process_response(user_resp)
            
            if not result['success']:
                return result

            settings_resp = requests.get(
                f"{self._API_BASE}/users/@me/settings",
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            
            user_data = result['data']
            nitro_mapping = {
                0: "NO_NITRO",
                1: "NITRO_CLASSIC",
                2: "NITRO",
                3: "NITRO_BASIC"
            }
            
            enhanced_data = {
                'locked': settings_resp.status_code != 200,
                'nitro_type': nitro_mapping.get(user_data.get('premium_type', 0)),
                'verification': {
                    'email': user_data.get('verified', False),
                    'phone': bool(user_data.get('phone'))
                }
            }
            
            result['data'] = {**user_data, **enhanced_data}
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def leave_guild(
        self,
        token: str,
        guild_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """Leaves a Discord server"""
        try:
            response = requests.delete(
                f"{self._API_BASE}/users/@me/guilds/{guild_id}",
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                json={"lurking": False},
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def rename_group(
        self,
        token: str,
        group_id: Snowflake,
        name: str,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Renames a Discord groupchat
        """

        try:
            response = requests.patch(
                f"{self._API_BASE}/channels/{group_id}",
                json={"name": name, **kwargs},
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def add_to_group(
        self,
        token: str,
        group_id: Snowflake,
        user_id: str,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Adds an user to a Discord groupchat
        """

        try:
            response = requests.put(
                f"{self._API_BASE}/channels/{group_id}/recipients/{user_id}",
                headers=self._headers.generate_headers(token, "Add Friends to DM"),
                json={**kwargs},
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def remove_from_group(
        self,
        token: str,
        group_id: Snowflake,
        user_id: str,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Removes an user to a Discord groupchat
        """

        try:
            response = requests.delete(
                f"{self._API_BASE}/channels/{group_id}/recipients/{user_id}",
                headers=self._headers.generate_headers(token),
                json={**kwargs},
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def add_note(
        self,
        token: str,
        user_id: Snowflake,
        text: str,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Adds a note to an user
        """

        try:
            response = requests.put(
                f"{self._API_BASE}/users/@me/notes/{user_id}",
                json={"note": text, **kwargs},
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def add_friend(
        self,
        token: str,
        user: str,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Sends a friend request 
        """

        try:
            response = requests.post(
                f"{self._API_BASE}/users/@me/relationships",
                json={"username": user, "discriminator": None, **kwargs},
                headers=self._headers.generate_headers(token, "Add Friend"),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }
        
    @_handle_rate_limits
    def remove_friend(
        self,
        token: str,
        user_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Removes a friend
        """

        try:
            response = requests.delete(
                f"{self._API_BASE}/users/@me/relationships/{user_id}",
                json={**kwargs},
                headers=self._headers.generate_headers(token, "Friends"),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def typing(
        self,
        token: str,
        channel_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Starts typing indicator
        """

        try:
            response = requests.post(
                f"{self._API_BASE}/channels/{channel_id}/typing",
                json={**kwargs},
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def leave_group(
        self,
        token: str,
        channel_id: Snowflake,
        silent: Optional[bool] = False,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """Leave a group chat"""
        try:
            response = requests.delete(
                f"{self._API_BASE}/channels/{channel_id}?silent={silent}",
                json={"silent": silent, **kwargs},
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }
        
    @_handle_rate_limits
    def create_group(
        self,
        token: str,
        channel_id: Snowflake,
        user_ids: List[Snowflake],
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Creates a group chat and adds users to it
        """
    
        if len(user_ids) > 9:
            return {
                'success': False,
                'error': {
                    'type': 'TooManyUsers',
                    'message': 'Cannot add more than 9 users to a group chat.'
                },
                'status_code': 400
            }
        if not user_ids:
            return {
                'success': False,
                'error': {
                    'type': 'NoUsersProvided',
                    'message': 'At least one user ID must be provided.'
                },
                'status_code': 400
            }
    
        try:
            headers = self._headers.generate_headers(token, "Add Friends to DM")
            proxies = proxy or {}
    
            first_user_id = user_ids[0]
            response = requests.put(
                f"{self._API_BASE}/channels/{channel_id}/recipients/{first_user_id}",
                json={**kwargs},
                headers=headers,
                impersonate=self._headers.impersonate_target,
                proxies=proxies
            )
            processed_response = self._process_response(response)
            if not processed_response.get('success', False):
                return processed_response
            
            if processed_response:
                new_channel_id = response.json().get('id')

            if not new_channel_id:
                return {
                    'success': False,
                    'error': {
                        'type': 'InvalidResponse',
                        'message': 'Failed to retrieve new channel ID from initial request.'
                    },
                    'status_code': processed_response.get('status_code', 0)
                }
    
            last_response = processed_response
            for user_id in user_ids[1:]:
                response = requests.put(
                    f"{self._API_BASE}/channels/{new_channel_id}/recipients/{user_id}",
                    json={**kwargs},
                    headers=headers,
                    impersonate=self._headers.impersonate_target,
                    proxies=proxies
                )
                processed_response = self._process_response(response)
                last_response = processed_response
                if not processed_response.get('success', False):
                    return processed_response
    
            return last_response
    
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }

    @_handle_rate_limits
    def open_dm(
        self,
        token: str,
        user_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> DiscordAPIResponse:
        """
        Opens a DM channel with a user.
        """
    
        try:
            response = requests.post(
                f"{self._API_BASE}/users/@me/channels",
                json={"recipients": [user_id], **kwargs},
                headers=self._headers.generate_headers(token, "{}"),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0
            }