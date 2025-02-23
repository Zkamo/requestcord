from requestcord import Build, Session

# Build Class Examples
# --------------------

# 1. Get individual build numbers
web_build = Build.get_web()
x86_version = Build.get_app("x86")
native_build = Build.get_native()

print(f"Web Build: {web_build}")
print(f"x86 Version: {x86_version}")
print(f"Native Build: {native_build}")

# 2. Get all build numbers at once
build = Build()
all_builds = build.build_numbers()
print(f"All Builds (Web, x86, Native): {all_builds}")

# Session Class Example
# ---------------------

# Initialize session with current web build
session = Session()

try:
    # Get session ID using valid token
    session_id = session.get_session("USER_TOKEN_HERE")
    print(f"Obtained Session ID: {session_id}")
    
except ConnectionError as e:
    print(f"Connection failed: {str(e)}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")