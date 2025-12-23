import re
import os
import base64
import secrets
import json
import mimetypes
import urllib.parse

import websocket

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

from ..common.response import APIResponse
from .constants import DISCORD_GATEWAY



class EmojiEncoder:
    """
    Helper to encode emoji for Discord API URLs.
    Handles both Unicode and custom emojis.
    """

    CUSTOM_EMOJI_REGEX = re.compile(r"<:(\w+):(\d+)>")
    ANIMATED_EMOJI_REGEX = re.compile(r"<a:(\w+):(\d+)>")

    @staticmethod
    def encode(emoji: str) -> str:
        """
        Returns the properly URL-encoded emoji string for regular reactions.
        """
        match = EmojiEncoder.CUSTOM_EMOJI_REGEX.match(emoji)
        if match:
            name, emoji_id = match.groups()
            return f"{name}:{emoji_id}"
        else:
            return urllib.parse.quote(emoji)

    @staticmethod
    def encode_super(emoji: str) -> str:
        """
        Returns the properly URL-encoded emoji string for SUPER reactions.
        For SUPER reactions, custom emojis need to be encoded differently.
        """
        match = EmojiEncoder.ANIMATED_EMOJI_REGEX.match(emoji)
        if match:
            name, emoji_id = match.groups()
            return urllib.parse.quote(f"{name}:{emoji_id}")
        
        match = EmojiEncoder.CUSTOM_EMOJI_REGEX.match(emoji)
        if match:
            name, emoji_id = match.groups()
            return urllib.parse.quote(f"{name}:{emoji_id}")
        
        return urllib.parse.quote(emoji)

class DiscordFileEncoder:
    """
    Encodes local files or URLs into Discord-compatible data URIs.
    """

    @staticmethod
    def encode(source: str) -> APIResponse:
        try:
            if DiscordFileEncoder._is_url(source):
                data, mime = DiscordFileEncoder._from_url(source)
            else:
                data, mime = DiscordFileEncoder._from_file(source)
    
            b64 = base64.b64encode(data).decode("utf-8")
            return APIResponse(
                success=True,
                status_code=200,
                data=f"data:{mime};base64,{b64}",
                error=None
            )
    
        except Exception as exc:
            return APIResponse(
                success=False,
                status_code=0,
                data=None,
                error=str(exc)
            )

    @staticmethod
    def _from_file(path: str) -> tuple[bytes, str]:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

        mime, _ = mimetypes.guess_type(path)
        if not mime:
            raise ValueError("Unsupported or unknown file type")

        with open(path, "rb") as f:
            return f.read(), mime

    @staticmethod
    def _from_url(url: str) -> tuple[bytes, str]:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()

            mime = r.headers.get("Content-Type")
            if not mime or not mime.startswith("image/"):
                raise ValueError("URL does not point to a valid image")

            return r.content, mime

        except RequestException as e:
            raise RuntimeError(f"Failed to fetch URL: {e}")

    @staticmethod
    def _is_url(value: str) -> bool:
        parsed = urllib.parse.urlparse(value)
        return parsed.scheme in ("http", "https")
    

class DiscordUtils:
    
    @staticmethod
    def get_web() -> APIResponse:
        try:
            page = requests.get("https://discord.com/app").text
            assets = re.findall(r'src="/assets/([^"]+)"', page)
    
            for asset in reversed(assets):
                js = requests.get(f"https://discord.com/assets/{asset}").text
                if "buildNumber:" in js:
                    return APIResponse(
                        success=True,
                        status_code=200,
                        data=int(js.split('buildNumber:"')[1].split('"')[0]),
                        error=None
                    )
    
            return APIResponse(
                success=False,
                status_code=0,
                data=None,
                error="Build number not found"
            )

        except RequestException as exc:
            return APIResponse(
                success=False,
                status_code=0,
                data=None,
                error=str(exc)
            )

    @staticmethod
    def fetch_session_id(token: str, fallback: bool = True) -> APIResponse:
        """
        Fetch a session_id from Discord gateway. If fails and fallback=True, generate a random one.

        Returns:
            APIResponse:
                - success: True if real session_id fetched, False if fallback/random used
                - data: {"session_id": str, "ws": WebSocket | None}
                - error: str if real fetch failed
        """
        try:
            ws = websocket.WebSocket()
            ws.connect(DISCORD_GATEWAY, timeout=10)

            hello = json.loads(ws.recv())
            heartbeat_interval = hello["d"]["heartbeat_interval"] / 1000

            payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "Windows"},
                },
            }
            ws.send(json.dumps(payload))

            while True:
                response = json.loads(ws.recv())

                if response.get("t") == "READY":
                    session_id = response["d"]["session_id"]
                    return APIResponse(
                        success=True,
                        status_code=200,
                        data={
                            "session_id": session_id,
                            "ws": ws,
                            "heartbeat_interval": heartbeat_interval
                        },
                        error=None
                    )

                if response.get("op") in (9, 429):
                    break

        except Exception as exc:
            error = str(exc)

        if fallback:
            random_session_id = secrets.token_hex(16)
            return APIResponse(
                success=False,
                status_code=0,
                data={"session_id": random_session_id, "ws": None},
                error=f"Failed to fetch real session_id: {error if 'error' in locals() else 'Unknown'}, fallback used"
            )

        return APIResponse(
            success=False,
            status_code=0,
            data=None,
            error=f"Failed to fetch session_id: {error if 'error' in locals() else 'Unknown'}"
        )