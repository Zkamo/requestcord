DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=9&encoding=json"
DISCORD_API = "https://discord.com/api/v9"

HEARTBEAT_INTERVAL = 45000
RECONNECT_DELAY = 5
MAX_RECONNECT_ATTEMPTS = 5

MAX_PRESENCE_SIZE = 128
MAX_CONNECT_QUEUE_SIZE = 100

OPCODES = {
    0: "DISPATCH",
    1: "HEARTBEAT",
    2: "IDENTIFY",
    3: "PRESENCE_UPDATE",
    4: "VOICE_STATE_UPDATE",
    5: "VOICE_SERVER_PING",
    6: "RESUME",
    7: "RECONNECT",
    8: "REQUEST_GUILD_MEMBERS",
    9: "INVALID_SESSION",
    10: "HELLO",
    11: "HEARTBEAT_ACK",
}
GATEWAY_CLOSE_CODES = {
    4000: "Unknown error",
    4001: "Unknown opcode",
    4002: "Decode error",
    4003: "Not authenticated",
    4004: "Authentication failed",
    4005: "Already authenticated",
    4007: "Invalid seq",
    4008: "Rate limited",
    4009: "Session timed out",
    4010: "Invalid shard",
    4011: "Sharding required",
    4012: "Invalid API version",
    4013: "Invalid intent(s)",
    4014: "Disallowed intent(s)",
}
INTENTS = {
    "GUILDS": 1 << 0,
    "GUILD_MEMBERS": 1 << 1,
    "GUILD_BANS": 1 << 2,
    "GUILD_EMOJIS_AND_STICKERS": 1 << 3,
    "GUILD_INTEGRATIONS": 1 << 4,
    "GUILD_WEBHOOKS": 1 << 5,
    "GUILD_INVITES": 1 << 6,
    "GUILD_VOICE_STATES": 1 << 7,
    "GUILD_PRESENCES": 1 << 8,
    "GUILD_MESSAGES": 1 << 9,
    "GUILD_MESSAGE_REACTIONS": 1 << 10,
    "GUILD_MESSAGE_TYPING": 1 << 11,
    "DIRECT_MESSAGES": 1 << 12,
    "DIRECT_MESSAGE_REACTIONS": 1 << 13,
    "DIRECT_MESSAGE_TYPING": 1 << 14,
    "MESSAGE_CONTENT": 1 << 15,
    "GUILD_SCHEDULED_EVENTS": 1 << 16,
    "AUTO_MODERATION_CONFIGURATION": 1 << 17,
    "AUTO_MODERATION_EXECUTION": 1 << 18,
}

DEFAULT_INTENTS = INTENTS["GUILDS"] | INTENTS["GUILD_MESSAGES"] | INTENTS["DIRECT_MESSAGES"]
ALL_NON_PRIVILEGED_INTENTS = (
    INTENTS["GUILDS"] |
    INTENTS["GUILD_BANS"] |
    INTENTS["GUILD_EMOJIS_AND_STICKERS"] |
    INTENTS["GUILD_INTEGRATIONS"] |
    INTENTS["GUILD_WEBHOOKS"] |
    INTENTS["GUILD_INVITES"] |
    INTENTS["GUILD_VOICE_STATES"] |
    INTENTS["GUILD_MESSAGES"] |
    INTENTS["GUILD_MESSAGE_REACTIONS"] |
    INTENTS["GUILD_MESSAGE_TYPING"] |
    INTENTS["DIRECT_MESSAGES"] |
    INTENTS["DIRECT_MESSAGE_REACTIONS"] |
    INTENTS["DIRECT_MESSAGE_TYPING"] |
    INTENTS["GUILD_SCHEDULED_EVENTS"] |
    INTENTS["AUTO_MODERATION_CONFIGURATION"] |
    INTENTS["AUTO_MODERATION_EXECUTION"]
)

PRESENCE_STATUS = ["online", "idle", "dnd", "offline"]
PRESENCE_ACTIVITY_TYPES = {
    0: "playing",
    1: "streaming",
    2: "listening",
    3: "watching",
    4: "custom",
    5: "competing",
}