# Record the LinkedIn demo video (macOS)

## Before you record

1. Build and preview locally:
   ```bash
   npm run build
   npm run preview
   ```
2. Open **http://localhost:4173** in Chrome (full screen later).
3. Hide distractions: Do Not Disturb on, close Slack/email.

## Option 1 — Autoplay mode (easiest)

Open this URL — the demo runs itself (~90 seconds):

```
http://localhost:4173/?record=1
```

Then record the screen (steps below). No clicking needed.

## Option 2 — Manual click-through (more natural)

Follow this script while recording:

| Time | Action |
|------|--------|
| 0:00 | Show hero — read headline silently or narrate |
| 0:05 | Click **Start the 2-minute story** |
| 0:15 | Click **Next: See what goes wrong** |
| 0:20 | Click **▶ Play: Typical pilot** — let it finish |
| 0:45 | Click **▶ Next: See what works →** |
| 1:00 | Click **👤 You approve as VP Sales** |
| 1:15 | Click **See the results →** |
| 1:25 | Hold on results panel for 5 seconds |

**Total: ~90 seconds**

## Record on Mac (built-in, free)

1. Press **Cmd + Shift + 5**
2. Select **Record Selected Portion** or **Record Entire Screen**
3. Click **Options** → microphone if narrating; otherwise no mic is fine with LinkedIn captions
4. Click **Record**
5. Run the demo (autoplay or manual)
6. Click **Stop** in the menu bar
7. Video saves to Desktop as `.mov`

## Optional narration script (30 sec voiceover)

> "A retail buyer wants twenty-two percent off a four-hundred-eighty thousand dollar renewal. Most AI pilots auto-approve it — no rules, no audit trail. The production approach checks pricing policy, routes approvals in parallel, and keeps a human in the loop. Same deal — completely different outcome. Try the interactive demo — link in comments."

## Upload to LinkedIn

1. Create post → **Add a video** (not a link in the main post body)
2. Upload the `.mov` file
3. Paste your caption
4. Put the demo link in the **first comment**:
   `https://doublelbuildsai.github.io/agent-readiness-workbench/`

## Tips

- Record at **1440px** width or full screen — LinkedIn crops square on mobile but full video plays on desktop
- Keep mouse movements slow and deliberate if clicking manually
- End on the **"The bottom line"** results screen — that's your thumbnail moment