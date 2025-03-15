from time import sleep
from requestcord import Presence, Logger

# Initialize logger
logger = Logger(level='INF')

# Example 1: Set custom status with emoji
try:
    logger.info("Setting custom status...")
    Presence.online(
        token="USER_TOKEN_HERE",
        status=Presence.Status.DND,
        activity_type=Presence.ActivityType.CUSTOM,
        details="✨ Made by requestcord!"
    )
    sleep(60)  # Keep status active for 1 minute

except KeyboardInterrupt:
    logger.info("Interrupted by user")
finally:
    Presence.offline("USER_TOKEN_HERE")
    logger.success("Custom status cleared")

# Example 2: Game activity with rich presence
try:
    logger.info("Setting game activity...")
    Presence.online(
        token="USER_TOKEN_HERE",
        status=Presence.Status.ONLINE,
        activity_type=Presence.ActivityType.PLAYING,
        name="Minecraft",
        details="Survival Mode",
    )
    sleep(300)  # Keep status active for 5 minutes

except Exception as e:
    logger.error(f"Error: {e}")
finally:
    Presence.offline("USER_TOKEN_HERE")
    logger.success("Game activity cleared")

# Example 3: Streaming status with Twitch
try:
    logger.info("Setting streaming status...")
    Presence.online(
        token="USER_TOKEN_HERE",
        status=Presence.Status.IDLE,
        activity_type=Presence.ActivityType.STREAMING,
        name="Twitch",
        details="Live coding session!",
        url="https://twitch.tv/discord"
    )
    sleep(600)  # Keep status active for 10 minutes

except KeyboardInterrupt:
    logger.info("Stream interrupted")
finally:
    Presence.offline("USER_TOKEN_HERE")
    logger.success("Streaming status cleared")

# Example 4: Music listening status
try:
    logger.info("Setting music status...")
    Presence.online(
        token="USER_TOKEN_HERE",
        status=Presence.Status.INVISIBLE,
        activity_type=Presence.ActivityType.LISTENING,
        name="Spotify",
        details="Requestcord radio 📻"
    )
    sleep(1800)  # Keep status active for 30 minutes

except Exception as e:
    logger.error(f"Error: {e}")
finally:
    Presence.offline("USER_TOKEN_HERE")
    logger.success("Music status cleared")