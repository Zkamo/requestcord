from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any, Union
import time

from .utils import DiscordUtils

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


class OpCode(Enum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    VOICE_SERVER_PING = 5
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


@dataclass
class ClientProperties:
    os: str = "Windows"
    browser: str = "Chrome"
    device: str = ""
    system_locale: str = "en-US"
    browser_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    browser_version: str = "131.0.0.0"
    os_version: str = "10"
    client_build_number: int = DiscordUtils.get_web().data
    design_id: int = 0

    def to_dict(self):
        return asdict(self)


@dataclass
class Activity:
    """Activity for presence."""
    type: ActivityType
    name: Optional[str] = None
    details: Optional[str] = None
    url: Optional[str] = None
    state: Optional[str] = None
    created_at: Optional[int] = None
    timestamps: Optional[Dict[str, int]] = None
    application_id: Optional[str] = None
    emoji: Optional[Dict[str, str]] = None
    party: Optional[Dict[str, Any]] = None
    assets: Optional[Dict[str, Any]] = None
    secrets: Optional[Dict[str, str]] = None
    instance: Optional[bool] = None
    flags: Optional[int] = None
    buttons: Optional[List[Dict[str, str]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert activity to Discord API format."""
        activity = {"type": self.type.value}
        if self.name:
            activity["name"] = self.name[:128]
        if self.details:
            activity["details"] = self.details[:128]
        if self.type == ActivityType.STREAMING and self.url:
            activity["url"] = self.url
        if self.state:
            activity["state"] = self.state[:128]
        if self.created_at:
            activity["created_at"] = self.created_at
        if self.timestamps:
            activity["timestamps"] = self.timestamps
        if self.application_id:
            activity["application_id"] = self.application_id
        if self.emoji:
            activity["emoji"] = self.emoji
        if self.party:
            activity["party"] = self.party
        if self.assets:
            activity["assets"] = self.assets
        if self.secrets:
            activity["secrets"] = self.secrets
        if self.instance is not None:
            activity["instance"] = self.instance
        if self.flags is not None:
            activity["flags"] = self.flags
        if self.buttons:
            activity["buttons"] = self.buttons
        return activity


@dataclass
class PresencePayload:
    since: int
    activities: List[Activity]
    status: Status
    afk: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op": OpCode.PRESENCE_UPDATE.value,
            "d": {
                "since": self.since,
                "activities": [activity.to_dict() for activity in self.activities],
                "status": self.status.value,
                "afk": self.afk,
            },
        }

@dataclass
class IdentifyPayload:
    token: str
    properties: ClientProperties
    presence: PresencePayload
    compress: bool = False
    large_threshold: int = 250
    shard: Optional[List[int]] = None
    intents: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "token": self.token,
            "properties": self.properties.to_dict(),
            "presence": self.presence.to_dict()["d"],
            "compress": self.compress,
            "large_threshold": self.large_threshold,
        }
        
        if self.shard and len(self.shard) == 2:
            data["shard"] = self.shard
        
        if self.intents:
            data["intents"] = self.intents
        
        return {
            "op": OpCode.IDENTIFY.value,
            "d": data
        }

@dataclass
class GatewaySession:
    session_id: str
    sequence: Optional[int] = None
    resume_url: Optional[str] = None
    last_heartbeat: Optional[float] = None
    connected_at: Optional[float] = None
    
    def __post_init__(self):
        if self.connected_at is None:
            self.connected_at = time.time()
    
    @property
    def uptime(self) -> float:
        if self.connected_at:
            return time.time() - self.connected_at
        return 0.0

@dataclass
class HeartbeatInfo:
    interval: int = 45000
    last_sent: Optional[float] = None
    last_ack: Optional[float] = None
    ack_received: bool = True
    jitter: float = 0.0
    
    @property
    def latency(self) -> Optional[float]:
        if self.last_sent and self.last_ack:
            return (self.last_ack - self.last_sent) * 1000
        return None

@dataclass
class GatewayConfig:
    token: str
    intents: int = 0
    compress: bool = False
    large_threshold: int = 250
    shard: Optional[List[int]] = None
    presence: Optional[PresencePayload] = None
    properties: Optional[ClientProperties] = None
    
    def __post_init__(self):
        if self.presence is None:
            self.presence = PresencePayload(
                since=0,
                activities=[],
                status=Status.ONLINE
            )
        
        if self.properties is None:
            self.properties = ClientProperties()

@dataclass
class GatewayEvent:
    op: OpCode
    d: Optional[Union[Dict[str, Any], List[Any], int, None]] = None
    s: Optional[int] = None
    t: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class HelloEvent:
    heartbeat_interval: int
    _trace: Optional[List[str]] = None

@dataclass
class ReadyEvent:
    v: int
    user: Dict[str, Any]
    guilds: List[Dict[str, Any]]
    session_id: str
    resume_gateway_url: str
    shard: Optional[List[int]] = None
    application: Optional[Dict[str, Any]] = None

@dataclass
class ShardInfo:
    shard_id: int
    shard_count: int

class ConnectionState(Enum):
    DISCONNECTED = 0
    CONNECTING = 1
    IDENTIFYING = 2
    RESUMING = 3
    CONNECTED = 4
    RECONNECTING = 5


@dataclass
class EventHandler:
    callback: Any
    event_name: str
    priority: int = 0
    once: bool = False
    
    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)