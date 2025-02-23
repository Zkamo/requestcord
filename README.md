<p align="center">
  <a href="https://pypi.org/project/requestcord/">
    <img src="https://cdn3.emoji.gg/emojis/4592-developer-purple.png" alt="Logo" witdth width="120" height="120">
  </a>

  <h3 align="center">Requestcord<a</a></h3>

  <p align="center">
    Requestcord - Discord API Wrapper
  </p>
</p>
<br/>

## Key Features
  - `Unofficial API Wrapper` – Interact with Discord without official limitations.
  - `Automatic Header Building` – No need to manually set headers.
  - `Simplified Requests` – Easily change status, global name, avatar, and more.
  - `Lightweight & Fast` – Optimized for speed and efficiency.
  - `Async Support` – Fully asyncio compatible for smooth operations.
  - `WebSocket & REST API` – Seamless communication with Discord’s services.

## Installing
- Python **3.8 or higher** is required.
- A **virtual environment** is recommended, especially on Linux.

`To install the library, run:`

**Linux/macOS:**
```bash
python3 -m pip install -U requestcord
```

**Windows:**
```bash
py -3 -m pip install -U requestcord
```

#### Development Version
To install the latest development version:
```bash
git clone https://github.com/Zkamo/requestcord.git
cd requestcord
python3 -m pip install -U .
```

### Header Generation Example

```py
from requestcord import HeaderGenerator

header_gen = HeaderGenerator()

join_via_invite_headers = header_gen.generate_headers(
    token="USER_TOKEN",
    location="Join Guild",
    invite_code="nexustools"
)

## // EXAMPLE OUTPUT

{
   "accept":"*/*",
   "accept-encoding":"gzip, deflate, br, zstd",
   "Accept-Language":"en;q=1.0",
   "Authorization":"USER_TOKEN",
   "content-type":"application/json",
   "cookie":"__dcfduid=d8c8f6ccf1d511efbceaa680d6f051ff; __sdcfduid=d8c8f6ccf1d511efbceaa680d6f051ff7b2e3ddee8d25e8ec87197b6ecd2950dfc3bdd7c2482fc3a5089598a727836c8; __cfruid=d8f79dc68ff3a5de9f8ee8885600140bcc2e6abb-1740308623; _cfuvid=bJ5ZxSYAdc40awekzpsIsBeVvPdnRUCAFz_FP6rE8kE-1740308623982-0.0.1.1-604800000",
   "origin":"https://discord.com",
   "priority":"u=1, i",
   "sec-ch-ua":"\"Google Chrome\";v=\"120\", \"Chromium\";v=\"120\", \"Not/A)Brand\";v=\"99\"",
   "sec-ch-ua-mobile":"?0",
   "sec-ch-ua-platform":"\"Windows\"",
   "sec-fetch-dest":"empty",
   "sec-fetch-mode":"cors",
   "sec-fetch-site":"same-origin",
   "user-agent":"Mozilla/5.0 (Windows NT 11; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
   "x-debug-options":"bugReporterEnabled",
   "x-discord-locale":"en-US",
   "x-discord-timezone":"America/Los_Angeles",
   "x-super-properties":"eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTE7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMjAuMC4wLjAgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEyMC4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMSIsInJlZmVycmVyIjoiaHR0cHM6Ly9kaXNjb3JkLmNvbS8iLCJyZWZlcnJpbmdfZG9tYWluIjoiZGlzY29yZC5jb20iLCJzZWFyY2hfZW5naW5lIjoiZ29vZ2xlIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MzcwNTMzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsLCJoYXNfY2xpZW50X21vZHMiOmZhbHNlfQ==",
   "x-context-properties":"eyJsb2NhdGlvbiI6ICJKb2luIEd1aWxkIiwgImxvY2F0aW9uX2d1aWxkX2lkIjogIjEyNjEwMDEzMzUyNDc5OTkxMTYiLCAibG9jYXRpb25fY2hhbm5lbF9pZCI6ICIxMjYxMDE0ODQ0MzI5NjkzMzQ2IiwgImxvY2F0aW9uX2NoYW5uZWxfdHlwZSI6IDB9"
}
```

### Bypass Onboarding Example

```py
from requestcord import Bypass

guild_id_with_onboarding = "SERVER_ID_WITH_ONBOARDING"

## // First check if onboarding exists
onboarding_data = Bypass.fetch_onboarding_questions(
    token="USER_TOKEN_HERE",
    guild_id=guild_id_with_onboarding
)

if onboarding_data:
    ## // Automatically answer and submit
    success = Bypass.onboarding(
        token="USER_TOKEN_HERE",
        guild_id=guild_id_with_onboarding
    )
    if success:
        print("Bypassed Onboarding!")
else:
  print("Server doesn't have onboarding requirements")

## // EXAMPLE OUTPUT
Bypassed Onboarding!

```

## Credits

- `Developer & Owner` - Zkamo
- `Special Thanks` - cf-vatos

