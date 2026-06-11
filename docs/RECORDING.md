# Record the LinkedIn demo video (macOS)

## Option 1 — Fully automated (recommended)

One command builds the static site, runs the autoplay demo in a headless browser, and saves a video:

```bash
bash scripts/record-demo.sh
```

Output: `recordings/agent-readiness-demo-YYYYMMDD-HHMMSS.webm` (or `.mp4` if `ffmpeg` is installed).

Options:

```bash
bash scripts/record-demo.sh              # default, ~70 seconds (hero + deal + agents)
bash scripts/record-demo.sh --pace 4     # slower agent steps, ~85 seconds
bash scripts/record-demo.sh --hold 5   # extra seconds on results screen
```

First run installs Playwright + Chromium automatically.

## Option 2 — Manual screen capture

1. Build and preview locally:
   ```bash
   python3 scripts/build-static.py
   bash scripts/preview-static.sh
   ```
2. Open **http://localhost:4173/?record=1** in Chrome (full screen).
3. Record with **Cmd + Shift + 5** while autoplay runs (~80 seconds).

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