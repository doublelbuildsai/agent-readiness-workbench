# LinkedIn launch checklist

## Is Render free?

Render has a free tier, but apps **sleep after 15 minutes** and take ~30s to wake — bad for LinkedIn clicks. Paid tier is ~$7/month.

**This project uses GitHub Pages (free, always on)** with a built-in static demo — no server needed.

## Your public demo URL

After deploying (see below):

```
https://doublelbuildsai.github.io/agent-readiness-workbench/
```

## Deploy to GitHub Pages (one-time)

```bash
cd /Users/Lawrence/Documents/personal_brand_building_AI/agent-readiness-workbench

# Initialize repo (first time only)
git init
git add .
git commit -m "Add agent readiness workbench executive demo"

# Create repo on GitHub: github.com/new → name: agent-readiness-workbench
git remote add origin https://github.com/doublelbuildsai/agent-readiness-workbench.git
git branch -M main
git push -u origin main
```

Then on GitHub:
1. **Settings → Pages**
2. Source: **GitHub Actions**
3. Wait ~2 min for workflow to finish
4. Visit your URL above

## Post structure

**Post body:** caption + native video (see RECORDING.md)

**First comment:**
```
▶ Try the interactive demo (2 min, no login):
https://doublelbuildsai.github.io/agent-readiness-workbench/

Click "Start the 2-minute story" → play both paths → see the results.

Built to show why enterprise AI pilots stall — and what production-ready revenue automation actually looks like.
```

## Recommended caption

```
Most enterprise AI pilots don't fail because the model is weak.

They fail because nobody would trust the output in a real approval chain.

I built a 2-minute side-by-side demo around a scenario every revenue leader knows:

A retail buyer asks for 22% off a $480K renewal. The rep needs a quote by Friday.

Typical AI pilot → auto-approves, ignores pricing rules, no audit trail.
Production-ready → policy checks, parallel approvals, human sign-off.

The question isn't "Can AI do this?"
It's "Would RevOps and Finance actually sign off?"

Try it — link in comments. What blocked your last AI pilot from production?
```