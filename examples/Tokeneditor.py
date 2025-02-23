from requestcord import ProfileEditor, ServerEditor

# Profile Editor Examples (works without Nitro)
# ------------------------

# 1. Change global avatar (profile picture)
ProfileEditor.change_avatar(
    token="USER_TOKEN_HERE",
    link="https://example.com/new_avatar.png"
)

# 2. Change display name (global name)
ProfileEditor.change_display(
    token="USER_TOKEN_HERE",
    name="New Display Name"
)

# 3. Change pronouns (appears in profile)
ProfileEditor.change_pronouns(
    token="USER_TOKEN_HERE",
    pronouns="they/them"
)

# 4. Change About Me section (bio)
ProfileEditor.change_about_me(
    token="USER_TOKEN_HERE",
    about_me="🌟 Coding enthusiast | 🎮 Gamer | 🌍 Traveler"
)

# 5. Change status with custom text and emoji
ProfileEditor.change_status(
    token="USER_TOKEN_HERE",
    status_type="dnd",  # online/idle/dnd/invisible
    custom_text="Busy coding",
    emoji={
        'name': '💻',  # Unicode emoji
        'id': None     # ID required for custom emojis
    }
)

# Server Editor Examples (Requires Nitro for server avatars)
# ----------------------

# 1. Change server-specific avatar (server profile picture) // nitro required
ServerEditor.change_avatar(
    token="USER_TOKEN_HERE",
    guild_id="SERVER_ID_HERE",
    link="https://example.com/server_avatar.png"
)

# 2. Change server nickname (nick name)
ServerEditor.change_nick(
    token="USER_TOKEN_HERE",
    guild_id="SERVER_ID_HERE",
    nick="[VIP] Cool User"
)