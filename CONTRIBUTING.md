# Contributing: forks, upstream, and pull requests

Everyone on the project works on their **own fork** and sends changes back to the
**original repo** with a pull request (PR).

| Name | What it is | URL |
|---|---|---|
| **upstream** | The original club repo (the "source of truth") | `github.com/data-science-ucsb/sports-stats-explorer` |
| **origin** | *Your* fork on GitHub | `github.com/<your-username>/sports-stats-explorer` |
| **local** | The copy on your laptop | — |

```
   upstream (club repo)
        │   ▲
  pull  │   │  pull request (on GitHub)
        ▼   │
     local ──push──► origin (your fork)
```

---

## 1. One-time setup

> Already forked and cloned? Skip to step **1c**.

**a. Fork** — on the [club repo](https://github.com/data-science-ucsb/sports-stats-explorer),
click **Fork** (top right).

**b. Clone your fork:**
```bash
git clone https://github.com/<your-username>/sports-stats-explorer.git
cd sports-stats-explorer
```

**c. Add the club repo as `upstream`:**
```bash
git remote add upstream https://github.com/data-science-ucsb/sports-stats-explorer.git
# (using SSH keys? use git@github.com:data-science-ucsb/sports-stats-explorer.git instead)
```

**d. Check it worked:**
```bash
git remote -v
# origin    https://github.com/<your-username>/sports-stats-explorer.git (fetch)
# origin    https://github.com/<your-username>/sports-stats-explorer.git (push)
# upstream  https://github.com/data-science-ucsb/sports-stats-explorer.git (fetch)
# upstream  https://github.com/data-science-ucsb/sports-stats-explorer.git (push)
```

---

## 2. Get the latest code from upstream  ⭐ do this often

**If you forked before the starter code was added, do this now** — your fork only
has the old README.

```bash
git checkout main
git pull upstream main      # download + merge the club repo's latest main
git push origin main        # update your fork on GitHub too
```

Do this **every time you start working** and **before opening a PR**.

> 💡 GitHub shortcut: on your fork's page, click **Sync fork → Update branch**.
> Then run `git pull` on your laptop.

After pulling, if `requirements.txt` or the data changed:
```bash
pip install -r requirements.txt
python scripts/load_data.py
```

---

## 3. Make a change

```bash
# Start from an up-to-date main
git checkout main
git pull upstream main

# Make a branch named after what you're doing
git checkout -b team-standings

# ...edit files, run `pytest` and `streamlit run app/Home.py`...

git add sql/team_standings.sql app/pages/2_Standings.py
git commit -m "Add team standings query and win % chart"
git push origin team-standings
```

## 4. Open a pull request

1. Go to your fork on GitHub — you'll see a **Compare & pull request** button.
2. Make sure it says **base: `data-science-ucsb/main`** ← **compare: `your-branch`**.
3. Fill in the template (what you did + a screenshot) and submit.
4. A project lead reviews it. If they ask for changes, just commit and push to the
   same branch — the PR updates automatically.

---

## Fixing merge conflicts

If `git pull upstream main` says **CONFLICT**:
1. Open the file(s) it lists. Look for `<<<<<<<`, `=======`, `>>>>>>>`.
2. Keep the code you want, delete the markers.
3. `git add <file>` then `git commit`.

Stuck? Ask in the club channel — conflicts happen to everyone.

---

## Ground rules

- **Never commit directly to `main`** — always use a branch.
- **One task per PR.** Small PRs get reviewed faster.
- **Claim a task** before starting (comment on the issue or tell the group) so two
  people don't build the same page.
- **Don't commit `db/league.db` or `.venv/`** — they're in `.gitignore` already.
- Make sure `pytest` passes before opening a PR.
