from requestcord import APIRequests

# // Initialize APIRequests Class
client = APIRequests()

# // Create Message Example
result = client.create_message(
    token="USER_TOKEN_HERE",
    channel_id=123456789,
    content="We love the best Discord API Wrapper, Requestcord"
)

# // Create Poll Example
result = client.create_poll(
    token="USER_TOKEN_HERE",
    channel_id=123456789,
    question="Is Requestcord the best Discord API Wrapper?",
    answers=[
        {"poll_media": {"text": "yes", "emoji": {"name": "✅"}}},
        {"poll_media": {"text": "no (yes)", "emoji": {"name": "❌"}}}
    ],
    duration=24  # in hours
)

# // Add Reaction Example
result = client.add_reaction(
    token="USER_TOKEN_HERE",
    channel_id=123456789,
    message_id=123456789,
    emoji="✅"
)

# // Delete Message Example
result = client.delete_message(
    token="USER_TOKEN_HERE",
    channel_id=123456789,
    message_id=123456789
)

# // Leave Server Example
result = client.leave_guild(
    token="USER_TOKEN_HERE",
    guild_id=123456789
)

# // Check Token Example
result = client.check_token(
    token="USER_TOKEN_HERE"
)

# // Rename Groupchat Example
result = client.rename_group(
    token="USER_TOKEN_HERE",
    group_id=123456789,
    name="Requestcord is the best discord API Wrapper!",
)

# // Add User To Groupchat Example
result = client.add_to_group(
    token="USER_TOKEN_HERE",
    group_id=123456789,
    user_id=123456789,
)

# // Remove User From Groupchat Example
result = client.remove_from_group(
    token="USER_TOKEN_HERE",
    group_id=123456789,
    user_id=123456789,
)

# // Add Note Example
result = client.add_note(
    token="USER_TOKEN_HERE",
    user_id=123456789,
    text="RequestCord On Top!"
)