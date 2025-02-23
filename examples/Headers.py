from requestcord import HeaderGenerator

# Initialize header generator
header_gen = HeaderGenerator()

# 1. Basic headers without context properties
basic_headers = header_gen.generate_headers(token="USER_TOKEN")
# Use case: General API requests without specific context

# 2. Joining a guild via invite code
join_via_invite_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="Join Guild",
    invite_code="nexustools"
)
# Use case: When accepting an invite through the API

# 3. Joining guild with known parameters
join_with_ids_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="Join Guild",
    guild_id="123456789012345678",
    channel_id="987654321098765432",
    channel_type=0  # 0 = text channel
)
# Use case: When you already have guild/channel info

# 4. Adding a friend
add_friend_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="Add Friend"
)
# Use case: Sending friend requests

# 5. User profile interaction
profile_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="User Profile"
)
# Use case: Viewing/modifying user profiles

# 6. Guild member list context
member_list_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="Guild Member List"
)
# Use case: Accessing server member lists

# 7. Friend request settings
friend_settings_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="Friend Request Settings"
)
# Use case: Managing friend request preferences

# 8. Bite-sized profile popout
popout_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="bite size profile popout"  # Note exact string match
)
# Use case: Interacting with user popout cards