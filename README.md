# Go Redirect Router (Edge Keyword: go)

Local Flask router that receives queries from an Edge custom search keyword and redirects based on rules in `rules.json`.

## What this does

- Listens on `127.0.0.1:5000`.
- Handles `GET /go?q=<query>`.
- Loads redirect rules from `rules.json`.
- Supports `GET /reload` to reload `rules.json` without restarting.
- Falls back to default search safely if rules are missing or invalid.

## Requirements

- Python 3.10+
- Flask installed in your environment

## Run manually

### Windows (PowerShell)

```powershell
cd "C:\Users\asus\OneDrive\Desktop\All Desktop Folders\go links"
.\env\Scripts\Activate.ps1
python app.py
```

### macOS (Terminal)

```bash
cd "/Users/<your-user>/OneDrive/Desktop/All Desktop Folders/go links"
source env/bin/activate
python app.py
```

## Edge keyword setup (one-time)

Create a custom search engine in Edge:

- Keyword: `go`
- URL: `http://127.0.0.1:5000/go?q=%s`

Then typing `go gmail 1 inbox` in the address bar sends `gmail 1 inbox` to this app.

## Rules file

`rules.json` must contain keys like:

- `escape_keyword`
- `default_search`
- `rules`

Use `http://127.0.0.1:5000/reload` after editing rules.

## Automate startup on Windows

Use Task Scheduler.

1. Open Task Scheduler.
2. Select Create Task.
3. In General:
- Name: `Go Links Router`
- Select Run only when user is logged on.
4. In Triggers:
- New trigger: At log on.
5. In Actions:
- Action: Start a program
- Program/script:
  `C:\Users\asus\OneDrive\Desktop\All Desktop Folders\go links\env\Scripts\python.exe`
- Add arguments:
  `"C:\Users\asus\OneDrive\Desktop\All Desktop Folders\go links\app.py"`
- Start in:
  `C:\Users\asus\OneDrive\Desktop\All Desktop Folders\go links`
6. Save the task.

Optional hidden startup:

- Use `pythonw.exe` instead of `python.exe` to avoid a terminal window.

## Automate startup on macOS

Use a Launch Agent (`launchd`).

1. Create folder if needed:

```bash
mkdir -p ~/Library/LaunchAgents
```

2. Create `~/Library/LaunchAgents/com.user.golinks.plist` with this content (update paths):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.user.golinks</string>

    <key>ProgramArguments</key>
    <array>
      <string>/Users/<your-user>/OneDrive/Desktop/All Desktop Folders/go links/env/bin/python</string>
      <string>/Users/<your-user>/OneDrive/Desktop/All Desktop Folders/go links/app.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/<your-user>/OneDrive/Desktop/All Desktop Folders/go links</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/golinks.out.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/golinks.err.log</string>
  </dict>
</plist>
```

3. Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.user.golinks.plist
```

4. Start now without relogin:

```bash
launchctl start com.user.golinks
```

5. Stop or unload when needed:

```bash
launchctl stop com.user.golinks
launchctl unload ~/Library/LaunchAgents/com.user.golinks.plist
```

## Quick checks

- Open `http://127.0.0.1:5000/go?q=gh`
- Open `http://127.0.0.1:5000/reload`
- If no redirect rule matches, it should redirect to your `default_search` from `rules.json`
