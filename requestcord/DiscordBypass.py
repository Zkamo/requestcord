from typing      import   Optional, Any, Dict, TypedDict, List, Tuple
from functools   import   wraps
from random      import   uniform, choice, sample, randint
from time        import   sleep, time
from datetime    import   datetime

from curl_cffi   import   requests

from requestcord import   Snowflake, HeaderGenerator, Logger

class DiscordAPIResponse(TypedDict):
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]
    status_code: int

class Bypass:
    _API_BASE: str = "https://discord.com/api/v9"
    _MAX_RETRY_ATTEMPTS: int = 3

    def __init__(self, logger: Optional[Logger] = None) -> None:
        self._headers = HeaderGenerator()
        self.logger = logger or Logger(level='INF')

    def _handle_rate_limits(func):
        """Handles Rate-Limitation from Discord."""
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
    def fetch_onboarding_questions(
        self,
        token: str,
        guild_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """
        Fetch onboarding questions for a guild.
        """
        endpoint = f"{self._API_BASE}/guilds/{guild_id}/onboarding"
        try:
            response = requests.get(
                endpoint,
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            result = self._process_response(response)
            if not result['success']:
                self.logger.error(
                    f"Failed to fetch onboarding questions: {result['status_code']} - "
                    f"{result.get('error', {}).get('message')}"
                )
            return result
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0,
                'data': None
            }

    def generate_random_responses(
        self,
        questions: Dict[str, Any]
    ) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
        """
        Generate random responses for onboarding questions.
        Returns:
            - List of selected option IDs
            - Dictionary of prompts seen with timestamps
            - Dictionary of options seen with timestamps
        """
        selected_options: List[str] = []
        prompts_seen: Dict[str, int] = {}
        options_seen: Dict[str, int] = {}
        current_time = int(time() * 1000)

        for prompt in questions.get("prompts", []):
            prompt_id = str(prompt.get("id"))
            prompts_seen[prompt_id] = current_time

            for option in prompt.get("options", []):
                option_id = str(option["id"])
                options_seen[option_id] = current_time

            if prompt["type"] == 0:
                options = prompt["options"]
                if prompt.get("single_select", True):
                    selected = [choice(options)["id"]]
                else:
                    selected = [opt["id"] for opt in sample(options, k=randint(1, len(options)))]
                selected_options.extend(selected)

        return selected_options, prompts_seen, options_seen

    @_handle_rate_limits
    def onboarding(
        self,
        token: str,
        guild_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """
        Full workflow to bypass onboarding.
        """
        onboarding_result = self.fetch_onboarding_questions(token, guild_id, proxy)
        if not onboarding_result['success']:
            return onboarding_result

        questions = onboarding_result['data']
        responses, prompts_seen, options_seen = self.generate_random_responses(questions)
        self.logger.debug(f"Submitting onboarding responses: {responses}")

        payload = {
            "onboarding_responses": responses,
            "onboarding_prompts_seen": prompts_seen,
            "onboarding_responses_seen": options_seen
        }

        endpoint = f"{self._API_BASE}/guilds/{guild_id}/onboarding-responses"
        try:
            response = requests.post(
                endpoint,
                headers=self._headers.generate_headers(token),
                json=payload,
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0,
                'data': None
            }

    @_handle_rate_limits
    def fetch_server_rules(
        self,
        token: str,
        guild_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """
        Get server verification requirements.
        """
        endpoint = f"{self._API_BASE}/guilds/{guild_id}/member-verification"
        try:
            response = requests.get(
                endpoint,
                headers=self._headers.generate_headers(token),
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            result = self._process_response(response)
            if not result['success']:
                self.logger.error(
                    f"Failed to fetch server rules: {result['status_code']} - "
                    f"{result.get('error', {}).get('message')}"
                )
            return result
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0,
                'data': None
            }

    def generate_rule_response(self, rules_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a payload that matches the server's verification form.
        """
        return {
            "version": rules_data.get("version"),
            "form_fields": [
                {
                    "field_type": field["field_type"],
                    "label": field["label"],
                    "description": field.get("description"),
                    "required": field["required"],
                    "values": field.get("values", []),
                    "response": True
                }
                for field in rules_data.get("form_fields", [])
                if field["field_type"] == "TERMS"
            ]
        }

    @_handle_rate_limits
    def server_rules(
        self,
        token: str,
        guild_id: Snowflake,
        proxy: Optional[Dict[str, str]] = None
    ) -> DiscordAPIResponse:
        """
        Full workflow to bypass server rules.
        """
        rules_result = self.fetch_server_rules(token, guild_id, proxy)
        if not rules_result['success']:
            return rules_result

        rules = rules_result['data']
        payload = self.generate_rule_response(rules)
        payload["additional_metadata"] = {
            "nonce": f"{randint(1000, 9999)}:{int(time() * 1000)}",
            "timestamp": datetime.now().isoformat()
        }

        endpoint = f"{self._API_BASE}/guilds/{guild_id}/requests/@me"
        try:
            response = requests.put(
                endpoint,
                headers=self._headers.generate_headers(token),
                json=payload,
                impersonate=self._headers.impersonate_target,
                proxies=proxy or {}
            )
            return self._process_response(response)
        except Exception as e:
            return {
                'success': False,
                'error': {'type': 'ConnectionError', 'message': str(e)},
                'status_code': 0,
                'data': None
            }
