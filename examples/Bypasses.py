from requestcord import Bypass

# Bypass Examples (you can add proxies)
# ------------------------

bypass = Bypass()

# 1. Bypass server onboarding questions
guild_id_with_onboarding = "SERVER_ID_WITH_ONBOARDING"

# Check onboarding requirements
onboarding_response = bypass.fetch_onboarding_questions(
    token="USER_TOKEN_HERE",
    guild_id=guild_id_with_onboarding
)

if onboarding_response['success'] and onboarding_response['data']:
    # Submit random responses
    submit_response = bypass.onboarding(
        token="USER_TOKEN_HERE",
        guild_id=guild_id_with_onboarding
    )
    
    if submit_response['success']:
        print("Successfully bypassed onboarding questions!")
    else:
        print(f"Failed to bypass onboarding: {submit_response['error']['message']}")
else:
    print("Server doesn't have onboarding or failed to fetch requirements")

# 2. Bypass server rules/verification
guild_id_with_rules = "SERVER_ID_WITH_VERIFICATION"

# Check verification requirements
rules_response = bypass.fetch_server_rules(
    token="USER_TOKEN_HERE",
    guild_id=guild_id_with_rules
)

if rules_response['success'] and rules_response['data']:
    # Accept verification rules
    verify_response = bypass.server_rules(
        token="USER_TOKEN_HERE",
        guild_id=guild_id_with_rules
    )
    
    if verify_response['success']:
        print("Successfully bypassed server verification!")
    else:
        print(f"Failed to bypass verification: {verify_response['error']['message']}")
else:
    print("Server doesn't have active verification or failed to fetch rules")
