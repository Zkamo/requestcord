from requestcord import Bypass

# Bypass Examples
# ------------------------

# 1. Bypass server onboarding questions
guild_id_with_onboarding = "SERVER_ID_WITH_ONBOARDING"

# First check if onboarding exists
onboarding_data = Bypass.fetch_onboarding_questions(
    token="USER_TOKEN_HERE",
    guild_id=guild_id_with_onboarding
)

if onboarding_data:
    # Automatically answer and submit
    success = Bypass.onboarding(
        token="USER_TOKEN_HERE",
        guild_id=guild_id_with_onboarding
    )
    if success:
        print("Bypassed onboarding!")
else:
    print("Server doesn't have onboarding requirements")

# 2. Bypass server rules/verification
guild_id_with_rules = "SERVER_ID_WITH_VERIFICATION"

# Check if server has rules verification
rules_data = Bypass.fetch_server_rules(
    token="USER_TOKEN_HERE",
    guild_id=guild_id_with_rules
)

if rules_data:
    # Automatically accept rules
    success = Bypass.server_rules(
        token="USER_TOKEN_HERE",
        guild_id=guild_id_with_rules
    )
    if success:
        print("Bypassed server rules successfully!")
else:
    print("Server doesn't have active verification")
