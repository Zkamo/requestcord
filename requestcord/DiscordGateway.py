from json                   import dumps, loads
from time                   import sleep, time
from enum                   import Enum
from threading              import Thread, Lock, Event
from typing                 import Dict, List, Optional

from websockets.sync.client import connect
from websockets.exceptions  import ConnectionClosed

from requestcord            import Logger, Build

logger = Logger(level='INF')

class Presence:
    """Main presence class containing nested enums"""
    
    class Status(Enum):
        ONLINE = "online"
        DND = "dnd"
        IDLE = "idle"
        INVISIBLE = "invisible"
        OFFLINE = "offline"

    class ActivityType(Enum):
        PLAYING = 0
        STREAMING = 1
        LISTENING = 2
        WATCHING = 3
        CUSTOM = 4
        COMPETING = 5

    _instances: Dict[str, 'Presence'] = {}
    _lock: Lock = Lock()

    def __init__(self, token: str):
        self.token = token
        self.status: Presence.Status = Presence.Status.ONLINE
        self.activities: List[dict] = []
        self.websocket = None
        self.heartbeat_interval: float = 30.0
        self.running = Event()
        self.thread: Optional[Thread] = None
        self.heartbeat_thread: Optional[Thread] = None

    @classmethod
    def online(
        cls,
        token: str,
        status: 'Presence.Status' = Status.ONLINE,
        activity_type: 'Presence.ActivityType' = ActivityType.CUSTOM,
        name: Optional[str] = None,
        details: Optional[str] = None,
        url: Optional[str] = None
    ) -> None:
        with cls._lock:
            if token not in cls._instances:
                instance = cls(token)
                cls._instances[token] = instance
    
            instance = cls._instances[token]
            instance._update_presence(
                status=status,
                activity_type=activity_type,
                name=name,
                details=details,
                url=url
            )
            
            if not instance.running.is_set():
                instance.start()

    @classmethod
    def offline(cls, token: str) -> None:
        with cls._lock:
            if token in cls._instances:
                instance = cls._instances.pop(token)
                instance.stop()

    def start(self):
        """Start presence connection"""
        if not self.running.is_set():
            self.running.set()
            self.thread = Thread(target=self._connection_loop)
            self.thread.start()

    def stop(self):
        """Force immediate disconnection"""
        if self.running.is_set():
            self.running.clear()
            
            if self.websocket:
                try:
                    self.websocket.close(code=1000)
                except Exception as e:
                    logger.error(f"Close error: {e}")
            
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=1)

    def _connection_loop(self):
        """Main connection manager with reconnection logic"""
        while self.running.is_set():
            try:
                with connect(
                    "wss://gateway.discord.gg/?v=9&encoding=json",
                    close_timeout=1
                ) as ws:
                    self.websocket = ws
                    self._initialize_connection()
                    self._message_loop()
            except Exception as e:
                if self.running.is_set():
                    logger.error(f"Connection error: {e}")
                    sleep(5)

    def _initialize_connection(self):
        """Perform handshake and authentication"""
        hello = loads(self.websocket.recv())
        self.heartbeat_interval = hello['d']['heartbeat_interval'] / 1000
        
        self.heartbeat_thread = Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
        
        auth_payload = self._build_auth_payload()
        self.websocket.send(dumps(auth_payload))

    def _message_loop(self):
        """Handle incoming messages"""
        while self.running.is_set() and self.websocket:
            try:
                message = loads(self.websocket.recv())
                self._handle_message(message)
            except ConnectionClosed:
                break
            except Exception as e:
                logger.error(f"Message error: {e}")
                break

    def _heartbeat_loop(self):
        last_presence_update = 0
        while self.running.is_set() and self.websocket:
            try:
                sleep(self.heartbeat_interval)
                
                self.websocket.send(dumps({"op": 1, "d": None}))
                
                if time() - last_presence_update > 30:
                    self._send_presence_update()
                    last_presence_update = time()
                    
            except ConnectionClosed:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break

    def _send_presence_update(self):
        if self.websocket:
            presence_update = {
                "op": 3,
                "d": {
                    "since": int(time() * 1000),
                    "activities": self.activities,
                    "status": self.status.value,
                    "afk": False
                }
            }
            try:
                self.websocket.send(dumps(presence_update))
                logger.info(f"Updated presence: {presence_update}")
            except Exception as e:
                logger.error(f"Presence update failed: {e}")

    def _build_auth_payload(self) -> dict:
        return {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "os": "Windows",
                    "browser": "Chrome",
                    "device": "",
                    "system_locale": "en-US",
                    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                    "browser_version": "113.0.0.0",
                    "os_version": "10",
                    "client_build_number": Build.get_web(),
                    "design_id": 0
                },
                "presence": {
                    "status": self.status.value,
                    "activities": self.activities,
                    "since": 0,
                    "afk": False
                }
            }
        }

    def _handle_message(self, message: dict):
        if message.get('op') == 11:
            pass 

    
    def _update_presence(
        self,
        status: 'Presence.Status',
        activity_type: 'Presence.ActivityType',
        name: Optional[str],
        details: Optional[str],
        url: Optional[str]
    ):
        self.status = status
        self.activities = []
        max_length = 128
    
        activity = {"type": activity_type.value}
    
        if activity_type == Presence.ActivityType.STREAMING:
            activity["name"] = "Twitch"
            if url:
                activity["url"] = url
            if details:
                activity["details"] = details[:max_length]
        elif activity_type == Presence.ActivityType.CUSTOM:
            activity["name"] = "Custom Status"
            if details:
                activity["state"] = details[:max_length]
        else:
            if name:
                activity["name"] = name[:max_length]
            if details:
                activity["details"] = details[:max_length]
    
        self.activities.append(activity)
    
        self._send_presence_update()