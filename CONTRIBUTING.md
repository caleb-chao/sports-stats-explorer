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

## 3. Track your work on the board

The **[project board](https://github.com/orgs/data-science-ucsb/projects/11)** shows who is working on what.
**You never drag cards yourself.** They move on their own when you do things on GitHub.

There are two kinds of cards:

| Card | What it is | How you get one |
|---|---|---|
| **Your take-home card** (label `take-home`) | Your own card for a workshop's take-home. Everyone makes one each week. | Click **Start your card** under the take-home in [ROADMAP.md](ROADMAP.md), then click **Create** at the bottom of the page. You don't need to type anything. |
| **Club task** (label `task`) | One piece of the club's dashboard, like a chart or a page. One person builds each one. | Comment `/claim` on the card. A bot replies to confirm it's yours. |

How cards move:

| When you... | ...the card moves to |
|---|---|
| Make a take-home card, or comment `/claim` on a club task | **In progress** |
| Open a pull request with `Closes #<card number>` in the description | **In review** |
| Get your pull request merged, or click **Close issue** on the card | **Done** |
| Comment `/unclaim` on a club task you changed your mind about | Back to **To do** |

> 💡 Open the **My cards** tab at the top of the board to see only your own cards.

The card number is the `#` number next to the card's title, like `#26`.

---

## 4. Make a change

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

## 5. Open a pull request

1. Go to your fork on GitHub — you'll see a **Compare & pull request** button.
2. Make sure it says **base: `data-science-ucsb/main`** ← **compare: `your-branch`**.
3. Fill in the template: what you did, `Closes #<card number>`, and a screenshot. Then submit.
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
- **Claim a club task** before starting (comment `/claim` on its card) so two
  people don't build the same page.
- **Don't commit `db/league.db` or `.venv/`** — they're in `.gitignore` already.
- Make sure `pytest` passes before opening a PR.

---

## For leads

- **Adding a club task:** open an issue with the **Task (shared club task)** template.
  It lands in **To do** on the board. Add a `workshop-N` label if it goes with a workshop,
  or `after-workshops` if several people should be able to claim it.
- **Assigning someone by hand** works too. The card moves to **In progress**.
- **Practice pull requests:** when you close a take-home pull request without merging
  it (after leaving feedback), the author's take-home card is closed and moved to
  **Done** for them.
- **How it works:** a GitHub Action ([`.github/workflows/board.yml`](.github/workflows/board.yml))
  does all the moving. Participants aren't org members, so they can't drag cards or
  assign themselves. The bot does it for them.
- **The `PROJECT_TOKEN` secret:** GitHub's built-in Actions token can't edit organization
  boards, so the Action uses this secret instead. Without it, `/claim` still assigns
  people, but cards don't move. If cards stop moving, the token has probably expired.
  To make a new one:
  1. Go to [github.com/settings/personal-access-tokens/new](https://github.com/settings/personal-access-tokens/new)
  2. **Resource owner:** `data-science-ucsb`. **Expiration:** the end of the quarter.
     **Repository access:** Public repositories.
  3. Under **Organization permissions**, set **Projects** to **Read and write**.
  4. Click **Generate token** and copy it.
  5. If GitHub says the token needs approval, approve it in the org's **Settings → Personal
     access tokens → Pending requests**.
  6. In this repo, go to **Settings → Secrets and variables → Actions**, and add or update
     the repository secret `PROJECT_TOKEN` with it.
