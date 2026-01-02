from __future__ import annotations

import time
import json
import base64
import uuid
import re
from typing import Optional

from platform import system, release
from curl_cffi import requests as curl_requests

from ..common.constants import DISCORD_API
from ..common.utils import DiscordUtils


_CHROME_RE = re.compile(r"Chrome/(\d+)")


class HeaderBuilder:
    def __init__(self):
        self._header_cache: dict = {}
        self._cookie_cache: dict = {}

        self._default_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def _extract_chrome_version(self, ua: str) -> int:
        match = _CHROME_RE.search(ua)
        return int(match.group(1)) if match else 120

    def _super_properties(self, user_agent: str, chrome_version: int) -> str:
        payload = {
            "os": system(),
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": user_agent,
            "browser_version": f"{chrome_version}.0.0.0",
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
            resp = curl_requests.get(
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

    def _resolve_invite(self, token: str, invite_code: str) -> dict:
        try:
            resp = curl_requests.get(
                f"{DISCORD_API}/invites/{invite_code}",
                headers={"Authorization": token},
                params={"with_counts": "true", "with_expiration": "true"},
                timeout=15
            )
            data = resp.json()
            return {
                "guild_id": data["guild"]["id"],
                "channel_id": data["channel"]["id"],
                "channel_type": data["channel"]["type"]
            }
        except Exception as e:
            raise ValueError(f"Invite resolution failed: {str(e)}")

    def _context_properties(self, location: str, **kwargs) -> str:
        """
        Generates Discord x-context-properties for any location.
        
        Special handling for 'Join Guild':
          - Use either invite_code OR guild_id/channel_id/channel_type.
        """
        if location == "{}":
            return "e30="
    
        context = {"location": location}
    
        if location == "Join Guild":
            if 'invite_code' in kwargs and any(k in kwargs for k in ['guild_id', 'channel_id', 'channel_type']):
                raise ValueError("Provide either invite_code OR guild_id/channel_id/channel_type, not both")
    
            if 'invite_code' in kwargs:
                if 'token' not in kwargs:
                    raise ValueError("Token is required to resolve invite_code")
                resolved = self._resolve_invite(kwargs['token'], kwargs['invite_code'])
                context.update({
                    "location_guild_id": resolved["guild_id"],
                    "location_channel_id": resolved["channel_id"],
                    "location_channel_type": resolved["channel_type"]
                })
            else:
                required = ['guild_id', 'channel_id', 'channel_type']
                if not all(k in kwargs for k in required):
                    raise ValueError(f"Join Guild requires {required} or invite_code")
                context.update({
                    "location_guild_id": str(kwargs["guild_id"]),
                    "location_channel_id": str(kwargs["channel_id"]),
                    "location_channel_type": int(kwargs["channel_type"])
                })
    
        return base64.b64encode(json.dumps(context).encode()).decode()

    def build(
        self,
        *,
        token: str,
        useragent: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, str]:
        ua = useragent or self._default_ua
        chrome_version = self._extract_chrome_version(ua)

        cache_key = f"{context or 'no_context'}:{ua}"
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
                    f'"Google Chrome";v="{chrome_version}", '
                    f'"Chromium";v="{chrome_version}", '
                    '"Not/A)Brand";v="99"'
                ),
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": ua,
                "x-debug-options": "bugReporterEnabled",
                "x-discord-locale": "en-US",
                "x-discord-timezone": "America/Los_Angeles",
                "x-super-properties": self._super_properties(
                    ua, chrome_version
                ),
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
