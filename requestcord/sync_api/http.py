from __future__ import annotations

import time
import json
import base64
import uuid
from typing import Any, Optional

from platform import system, release
from curl_cffi import requests as curl_requests

from ..common.response import APIResponse
from ..common.constants import DISCORD_API
from ..common.utils import DiscordUtils


class HeaderBuilder:
    def __init__(self, session: curl_requests.Session):
        self.session = session
        self._header_cache: dict = {}
        self._cookie_cache: dict = {}

        self.chrome_version = 120
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{self.chrome_version}.0.0.0 Safari/537.36"
        )


    def _super_properties(self) -> str:
        payload = {
            "os": system(),
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": self.user_agent,
            "browser_version": f"{self.chrome_version}.0.0.0",
            "os_version": release(),
            "referrer": "https://discord.com/",
            "referring_domain": "discord.com",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": DiscordUtils.get_web().data,
            "client_event_source": None,
            "has_client_mods": False,
            "client_launch_id": str(uuid.uuid4()),
            "launch_signature": str(uuid.uuid4()),
            "client_heartbeat_session_id": str(uuid.uuid4()),
            "client_app_state": "focused",
        }


        raw = json.dumps(payload, separators=(",", ":")).encode()
        return base64.b64encode(raw).decode()


    def _fetch_cookies(self, token: str) -> str:
        now = time.time()

        cached = self._cookie_cache.get(token)
        if cached and now - cached["ts"] < 86400:
            return cached["cookie"]

        try:
            resp = self.session.get(
                f"{DISCORD_API}/users/@me",
                headers={"Authorization": token},
                timeout=15,
            )

            cookies = []
            if "set-cookie" in resp.headers:
                for part in resp.headers["set-cookie"].split(", "):
                    cookie = part.split(";", 1)[0]
                    if "=" in cookie:
                        cookies.append(cookie)

            cookie_str = "; ".join(cookies)
            self._cookie_cache[token] = {"cookie": cookie_str, "ts": now}
            return cookie_str

        except Exception:
            return ""


    def _context_properties(self, location: str) -> str:
        payload = {"location": location}
        return base64.b64encode(json.dumps(payload).encode()).decode()


    def build(
        self,
        token: str,
        *,
        context: Optional[str] = None,
    ) -> dict[str, str]:
        cache_key = context or "no_context"
        now = time.time()

        cached = self._header_cache.get(cache_key)
        if cached and now - cached["ts"] < 86400:
            headers = cached["headers"].copy()
        else:
            headers = {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "origin": "https://discord.com",
                "referer": "https://discord.com/",
                "priority": "u=1, i",
                "sec-ch-ua": (
                    f'"Google Chrome";v="{self.chrome_version}", '
                    f'"Chromium";v="{self.chrome_version}", '
                    '"Not/A)Brand";v="99"'
                ),
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": self.user_agent,
                "x-debug-options": "bugReporterEnabled",
                "x-discord-locale": "en-US",
                "x-discord-timezone": "America/Los_Angeles",
                "x-super-properties": self._super_properties(),
            }

            if context:
                headers["x-context-properties"] = self._context_properties(context)

            self._header_cache[cache_key] = {
                "headers": headers.copy(),
                "ts": now,
            }

        headers["Authorization"] = token
        headers["cookie"] = self._fetch_cookies(token)

        return headers


class HTTPClient:
    def __init__(
        self,
        *,
        backend: str,
        proxy: Optional[str] = None,
        timeout: int = 30,
        debug: bool = False,
    ):
        if backend != "curl_cffi":
            raise ValueError("Only curl_cffi backend is supported")

        self.debug = debug

        self.session = curl_requests.Session(
            impersonate="chrome120",
            timeout=timeout,
        )

        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}

        self.headers = HeaderBuilder(self.session)

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: Optional[str] = None,
        json_data: Any = None,
        params: Optional[dict[str, Any]] = None,
        context: Optional[str] = None,
    ) -> APIResponse:
        url = DISCORD_API + path

        try:
            headers = (
                self.headers.build(token, context=context)
                if token
                else None
            )

            resp = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
            )

        except Exception as exc:
            return APIResponse(
                success=False,
                status_code=0,
                data=None,
                error=str(exc),
            )

        try:
            data = resp.json()
            parsed_json = True
        except ValueError:
            data = resp.text
            parsed_json = False
        except Exception as exc:
            return APIResponse(
                success=False,
                status_code=resp.status_code,
                data=None,
                error=f"Failed to parse response JSON: {exc}",
            )
        
        if not parsed_json and resp.status_code >= 400:
            return APIResponse(
                success=False,
                status_code=resp.status_code,
                data=data,
                error="Non-JSON error response from Discord (possible Cloudflare or proxy issue)",
            )

        if 200 <= resp.status_code < 300:
            return APIResponse(
                success=True,
                status_code=resp.status_code,
                data=data,
                error=None,
            )

        error_message = None

        if isinstance(data, dict):
            error_message = data.get("message")
            discord_code = data.get("code")

            if discord_code is not None:
                error_message = f"{error_message} (Discord code {discord_code})"

        if not error_message:
            error_message = resp.reason or "Unknown API error"


        return APIResponse(
            success=False,
            status_code=resp.status_code,
            data=data,
            error=error_message,
        )


    def get(
        self, 
        path: str, 
        *, 
        token: Optional[str] = None, 
        params: Optional[dict[str, Any]] = None
        ) -> APIResponse:
        return self._request(
            "GET", path, token=token, params=params
            )

    def post(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        json: Any = None,
        context: Optional[str] = None,
    ) -> APIResponse:
        return self._request(
            "POST", path, token=token, json_data=json, context=context
        )

    def put(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        json: Any = None,
        params: Optional[dict[str, Any]] = None,
        context: Optional[str] = None,
    ) -> APIResponse:
        return self._request(
            "PUT", path, token=token, json_data=json, params=params, context=context
        )

    def delete(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        json: Any = None,
        params: Optional[dict[str, Any]] = None,
        context: Optional[str] = None,
    ) -> APIResponse:
        return self._request(
            "DELETE", path, token=token, json_data=json, params=params, context=context
        )
        
    def patch(
        self,
        path: str,
        *,
        token: Optional[str] = None,
        json: Any = None,
        params: Optional[dict[str, Any]] = None,
        context: Optional[str] = None,
    ) -> APIResponse:
        return self._request(
            "PATCH", path, token=token, json_data=json, params=params, context=context
        )
        
    def close(self) -> None:
        try:
            self.session.close()
        except Exception:
            pass
