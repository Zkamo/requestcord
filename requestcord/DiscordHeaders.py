from requestcord import *
logger = Logger(level='INF')

class HeaderGenerator:
    SUPPORTED_CHROME_VERSIONS = [120, 119, 104]
    MAX_SUPPORTED_VERSION = max(SUPPORTED_CHROME_VERSIONS)

    def __init__(self):
        self.build_fetcher = Build()
        self.client_build_number = self._get_latest_build_number()
        self.base_chrome_version = self._get_chrome_version()
        self.impersonate_target = f"chrome{self.base_chrome_version}"
        self.session = requests.Session(impersonate=self.impersonate_target)
        self.ua_details = self._generate_ua_details()

    def _get_latest_build_number(self) -> int:
        """Get the most recent valid build number"""
        web_build, x86_build, native_build = self.build_fetcher.build_numbers()
        return web_build

    def _get_chrome_version(self) -> int:
        """Fetch and parse latest Chrome version with version clamping"""
        try:
            resp = requests.get(
                "https://chromiumdash.appspot.com/fetch_releases",
                params={"channel": "Stable", "platform": "Windows", "num": 1},
                timeout=10
            )
            data = resp.json()
            if data and isinstance(data, list):
                version_str = data[0].get('version', '125.0.0.0')
                fetched_version = int(version_str.split('.')[0])
                return min(fetched_version, self.MAX_SUPPORTED_VERSION)
            return self.MAX_SUPPORTED_VERSION
        except Exception as e:
            logger.error(f"Chrome version fetch failed: {e}, using fallback")
            return self.MAX_SUPPORTED_VERSION

    def _generate_ua_details(self) -> dict:
        """Generate browser details using supported Chrome version"""
        chrome_major = self.base_chrome_version
        full_version = f"{chrome_major}.0.0.0"
        
        os_spec = self._get_os_string()
        platform_ua = f"Windows NT {platform.release()}; Win64; x64" if "Windows" in os_spec else os_spec

        return {
            "user_agent": (
                f"Mozilla/5.0 ({platform_ua}) AppleWebKit/537.36 "
                f"(KHTML, like Gecko) Chrome/{full_version} Safari/537.36"
            ),
            "chrome_version": full_version,
            "sec_ch_ua": [
                f'"Google Chrome";v="{chrome_major}"',
                f'"Chromium";v="{chrome_major}"',
                '"Not/A)Brand";v="99"'
            ]
        }

    def _get_os_string(self) -> str:
        """Generate OS identifier string"""
        os_info = {
            "Windows": f"Windows NT 10.0; Win64; x64",
            "Linux": "X11; Linux x86_64",
            "Darwin": "Macintosh; Intel Mac OS X 10_15_7"
        }.get(platform.system(), "Windows NT 10.0; Win64; x64")
        
        if platform.system() == "Windows":
            win_ver = platform.version().split('.')
            os_info = f"Windows NT {win_ver[0]}.{win_ver[1]}; Win64; x64"
            
        return os_info

    def fetch_cookies(self, token: str) -> str:
        """Get fresh cookies using a token"""
        try:
            resp = self.session.get(
                "https://discord.com/api/v9/users/@me",
                headers={"Authorization": token},
                timeout=15
            )
            cookies = []
            if "set-cookie" in resp.headers:
                cookie_headers = resp.headers["set-cookie"].split(", ")
                for cookie in cookie_headers:
                    cookie_part = cookie.split(";")[0]
                    if "=" in cookie_part:
                        name, value = cookie_part.split("=", 1)
                        cookies.append(f"{name}={value}")
            return "; ".join(cookies)
        except Exception as e:
            logger.error(f"Cookie fetch failed: {e}")
            return ""

    def _resolve_invite(self, token: str, invite_code: str) -> dict:
        """Resolve invite with proper TLS impersonation"""
        try:
            resp = self.session.get(
                f"https://discord.com/api/v9/invites/{invite_code}",
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
    
    def generate_super_properties(self) -> str:
        """Generate x-super-properties header"""
        sp = {
            "os": platform.system(),
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": self.ua_details["user_agent"],
            "browser_version": self.ua_details["chrome_version"].split('.0.')[0] + ".0.0.0",
            "os_version": str(platform.release()),
            "referrer": "https://discord.com/",
            "referring_domain": "discord.com",
            "search_engine": "google",
            "release_channel": "stable",
            "client_build_number": self.client_build_number,
            "client_event_source": None,
            "has_client_mods": False
        }

        return base64.b64encode(json.dumps(sp, separators=(',', ':')).encode()).decode()

    def generate_context_properties(self, location: str, **kwargs) -> str:
        """Generate x-context-properties"""
        valid_locations = {
            "Add Friend", "User Profile", "Guild Member List",
            "Accept Invite Page", "DM Header", "Friend Request Settings",
            "bite size profile popout",
            "Join Guild"
        }
        
        if location not in valid_locations:
            raise ValueError(f"Invalid location: {location}. Valid options: {valid_locations}")
    
        context = {"location": location}
        
        if location == "Join Guild":
            if 'invite_code' in kwargs and any(k in kwargs for k in ['guild_id', 'channel_id', 'channel_type']):
                raise ValueError("Provide either invite_code OR guild_id/channel_id/channel_type, not both")
            
            if 'invite_code' in kwargs:
                resolved = self._resolve_invite(kwargs.get('token'), kwargs['invite_code'])
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

    def generate_headers(self, token: str, location: str = None, **kwargs) -> dict:
        """Generate complete headers"""
        headers = {
            'accept': '*/*',
            'accept-encoding' : 'gzip, deflate, br, zstd',
            'Accept-Language': 'en;q=1.0',
            "Authorization": token,
            'content-type': 'application/json',
            "cookie": self.fetch_cookies(token),
            'origin': 'https://discord.com',
            'priority': 'u=1, i',
            "sec-ch-ua": ", ".join(self.ua_details["sec_ch_ua"]),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            "user-agent": self.ua_details["user_agent"],
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "America/Los_Angeles",
            "x-super-properties": self.generate_super_properties()
        }
    
        if location:
            headers["x-context-properties"] = self.generate_context_properties(
                location, 
                token=token,
                **kwargs
            )
    
        return headers