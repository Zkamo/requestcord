from requestcord import ProfileEditor, ServerEditor

# Initialize editors with optional logger
profile_editor = ProfileEditor()
server_editor = ServerEditor()

# Optional proxy configuration
proxy = {
    "http": "http://username:password@proxy_ip:port",
    "https": "http://username:password@proxy_ip:port"
}

# Profile Editor Examples
# ------------------------

# 1. Change global avatar with optional proxy
avatar_response = profile_editor.change_avatar(
    token="USER_TOKEN_HERE",
    link="https://example.com/new_avatar.png",
    proxy=proxy  # Remove this parameter if not using proxy
)

if avatar_response['success']:
    print("✅ Avatar updated successfully!")
    print(f"New avatar hash: {avatar_response['data'].get('avatar')}")
else:
    print(f"❌ Avatar update failed: {avatar_response['error']['message']}")

# 2. Change display name
display_response = profile_editor.change_display(
    token="USER_TOKEN_HERE",
    name="New Display Name"
)

if display_response['success']:
    print("✅ Display name updated successfully!")
    print(f"New display name: {display_response['data'].get('global_name')}")
else:
    print(f"❌ Display name update failed: {display_response['error']['message']}")

# 3. Update pronouns through proxy
pronouns_response = profile_editor.change_pronouns(
    token="USER_TOKEN_HERE",
    pronouns="Request/Cord",
    proxy=proxy  # Works with or without this parameter
)

if pronouns_response['success']:
    print("✅ Pronouns updated successfully!")
    print(f"New pronouns: {pronouns_response['data'].get('pronouns')}")
else:
    print(f"❌ Pronouns update failed: {pronouns_response['error']['message']}")

# 4. Change About Me section
bio_response = profile_editor.change_about_me(
    token="USER_TOKEN_HERE",
    about_me="🌟 Coding enthusiast | 🎮 Gamer | 🌍 Traveler"
)

if bio_response['success']:
    print("✅ Bio updated successfully!")
    print(f"New bio: {bio_response['data'].get('bio')}")
else:
    print(f"❌ Bio update failed: {bio_response['error']['message']}")

# 5. Set custom status
status_response = profile_editor.change_status(
    token="USER_TOKEN_HERE",
    status_type="dnd",
    custom_text="Busy coding",
    emoji={
        'name': '💻',  # For custom emojis: 'name': 'emoji_name', 'id': 'emoji_id'
        'id': None
    },
    proxy=proxy  # Remove if not needed
)

if status_response['success']:
    print("✅ Status updated successfully!")
    print(f"New status: {status_response['data'].get('custom_status', {}).get('text')}")
else:
    print(f"❌ Status update failed: {status_response['error']['message']}")

# Server Editor Examples
# ------------------------

# 1. Change server avatar (Nitro required)
server_avatar_response = server_editor.change_avatar(
    token="USER_TOKEN_HERE",
    guild_id="SERVER_ID_HERE",
    link="https://example.com/server_avatar.png"
)

if server_avatar_response['success']:
    print("✅ Server avatar updated successfully!")
    print(f"New server avatar: {server_avatar_response['data'].get('avatar')}")
else:
    print(f"❌ Server avatar update failed: {server_avatar_response['error']['message']}")

# 2. Change server nickname
nick_response = server_editor.change_nick(
    token="USER_TOKEN_HERE",
    guild_id="SERVER_ID_HERE",
    nick="[VIP] Cool User"
)

if nick_response['success']:
    print("✅ Nickname updated successfully!")
    print(f"New nickname: {nick_response['data'].get('nick')}")
else:
    print(f"❌ Nickname update failed: {nick_response['error']['message']}")
