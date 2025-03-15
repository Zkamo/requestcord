from typing import NewType

Snowflake                         = NewType('Snowflake', int)

from requestcord.Logger           import Logger
from discord_protos               import PreloadedUserSettings
from requestcord.DiscordFetch     import Build
from requestcord.DiscordFetch     import SessionID
from requestcord.DiscordGateway   import Presence
from requestcord.DiscordHeaders   import HeaderGenerator
from requestcord.DiscordBypass    import Bypass
from requestcord.DiscordChange    import ServerEditor
from requestcord.DiscordChange    import ProfileEditor
from requestcord.DiscordRequests  import APIRequests
