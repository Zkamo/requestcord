from requestcord import *
logger = Logger(level='INF')

class Build:
    BASE_URL = "https://discord.com"
    WEB_APP_URL = f"{BASE_URL}/app"
    INSTALLER_API_URL = f"{BASE_URL}/api/downloads/distributions/app/installers/latest"

    @staticmethod
    def get_web() -> int:
        """Fetch the build number from the Discord web app page."""
        try:
            page = requests.get(Build.WEB_APP_URL).text
            assets = re.findall(r'src="/assets/([^"]+)"', page)
            
            for asset in reversed(assets):
                js = requests.get(f"{Build.BASE_URL}/assets/{asset}").text
                if "buildNumber:" in js:
                    return int(js.split('buildNumber:"')[1].split('"')[0])
            
        except requests.RequestException as e:
            logger.error(f"Error fetching build from web: {e}")
        
        return -1
    
    @staticmethod
    def get_app(arch: str) -> str:
        """Fetch the build version from the Discord API for the specified architecture."""
        try:
            response = requests.get(
                Build.INSTALLER_API_URL,
                params={"channel": "stable", "platform": "win", "arch": arch},
                allow_redirects=False
            )
            redirect_url = response.headers.get('Location', '')
            version_match = re.search(fr'{arch}/(.*?)/', redirect_url)
            return version_match.group(1) if version_match else ''
        
        except requests.RequestException as e:
            logger.error(f"Error fetching build from installer ({arch}): {e}")
            return -1

    @staticmethod
    def get_native() -> int:
        """Fetch the native build number from the x64 installer URL."""
        version = Build.get_app("x64")
        if version:
            build_number_str = version.split('.')[-1]
            try:
                return int(build_number_str)
            except ValueError:
                pass
        
        return -1

    def build_numbers(self) -> tuple[int, str, int]:
        """Fetch all build numbers: web, main, and native."""
        return (
            self.get_web(),
            self.get_app("x86"),
            self.get_native()
        )

class Session:
    def __init__(self):
        self.ws = WebSocket()
        self.current_build = Build.get_web()

    def get_session(self, token: str) -> str:
        """Get session ID"""
        self.ws.connect("wss://gateway.discord.gg/?encoding=json&v=9")
        
        hello = loads(self.ws.recv())
        
        auth_payload = {
            "op": 2,
            "d": {
                "token": token,
                "capabilities": 8189,
                "properties": {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": "",
                    "system_locale": "en-US",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                    "browser_version": "113.0.0.0",
                    "os_version": "10",
                    "client_build_number": self.current_build,
                    "design_id": 0
                },
                "presence": {
                    "status": "online",
                    "since": 0,
                    "activities": [],
                    "afk": False
                },
                "compress": False,
                "client_state": {
                    "guild_versions": {},
                    "highest_last_message_id": "0",
                    "read_state_version": 0,
                    "user_guild_settings_version": -1,
                    "user_settings_version": -1,
                    "private_channels_version": "0",
                    "api_code_version": 0
                }
            }
        }
        self.ws.send(dumps(auth_payload))

        while True:
            response = loads(self.ws.recv())
            if response.get('t') == 'READY':
                self.ws.close()
                return response['d']['session_id']
            if response.get('op') == 9:
                self.ws.close()
                raise ConnectionError("Invalid session")