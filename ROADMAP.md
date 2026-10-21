# Roadmap

This page shows what we will build, one workshop at a time.

**You do not need to read all of this today.** Find the workshop you are on, read that section, and ignore the rest until you get there.

---

## How this works

Each workshop has three parts:

1. **In the workshop** you learn one skill, like SQL or making charts.
2. **By the end of the workshop** you will have finished something small and real.
3. **The take-home** uses that same skill on the actual project code. It should take about an hour.

Every take-home has two levels. **Pick one:**

- **Starter:** the main task. Doing just this is plenty.
- **Challenge:** optional, for when you finish the Starter and want more.

Missed a workshop or fell behind? That's fine. Each take-home works on its own, so you can skip ahead and come back later.

---

## The plan at a glance

| Date | Workshop | Lead | By the end you will have | Take-home |
|---|---|---|---|---|
| 10/13 | 1. AI Vibecoding | Jakob | The dashboard running, and AI helping you read and write code | Write a leaderboard query with AI's help |
| 10/20 | 2. Project Management, Kanban, and PRs | Clement | A task claimed on the board and Git set up | Make your first pull request |
| 10/27 | 3. Data Analytics | Diego | Queries that combine tables, and a chart you made | Build the Player Profile query |
| 11/2 | 4. Classical ML | Jakob | A model that sorts or predicts things from data | Group players into "player types" |
| 11/9 | 5. Deployment | Clement | The dashboard online with a real link | Deploy your own copy |
| 11/16 | 6. How to Talk About Your Project | Sid | A clear way to explain what you built | Write your project pitch |

Dates may shift. This table is the plan, not a promise.

---

## Workshop 1: AI Vibecoding (10/13, Jakob)

**In the workshop:** use an AI coding assistant to understand code you didn't write, and to write new code by describing what you want in plain English.

**By the end you will have:**
- The dashboard running on your laptop with `streamlit run app/Home.py` (setup steps are in the [README](README.md#getting-started))
- Asked an AI to explain `sql/top_scorers.sql` line by line, and understood the answer

### Take-home 1: Write a leaderboard query with AI's help

The dashboard has a Top Scorers page. Make one for another stat.

**How the workshop helps:** give the AI `sql/top_scorers.sql` and `db/schema.sql`, and ask it to make a version for rebounds. Then check its work. The goal is to understand every line, not just paste it.

**Starter**

1. Copy `sql/top_scorers.sql` to a new file, `sql/top_rebounders.sql`
2. Change it to use `rebounds` instead of `points` (by hand or with AI)
3. Test it in `sqlite3`. The `:limit` and `:min_games` placeholders need values first:
   ```
   sqlite3 db/league.db
   .param set :limit 10
   .param set :min_games 5
   .read sql/top_rebounders.sql
   ```

**Done when:** the query lists the 10 best rebounders, highest first, and you can explain what `GROUP BY` and `AVG()` do in it.

**Challenge**

`app/Home.py` has a query written directly in Python (look for the `TODO` comment). Move it into a new file, `sql/league_summary.sql`, and change `Home.py` to use `run_query("league_summary")`, the same way the Top Scorers page does.

<details>
<summary>Stuck?</summary>

- Ask the AI to explain an error message. Paste the whole error, not just the last line.
- If the AI's code doesn't run, tell it what happened. It usually fixes it on the second try.
- Every column in `SELECT` must be either in the `GROUP BY` or inside a function like `SUM()` or `AVG()`.
- Try [SQLBolt lessons 1 to 4 and 10 to 12](https://sqlbolt.com/).
</details>

---

## Workshop 2: Project Management, Kanban, and PRs (10/20, Clement)

**In the workshop:** how a team splits up work. Use a Kanban board (To do, In progress, Done) to claim tasks, and use pull requests to get your work reviewed and merged.

**By the end you will have:**
- The `upstream` remote set up, so you can download new code from the club repo (see [CONTRIBUTING.md](CONTRIBUTING.md))
- A task claimed on the project board

### Take-home 2: Make your first pull request

You will practice the full Git workflow on something that can't break anything.

**Starter**

1. Make a branch: `git checkout -b add-<your-name>`
2. Create a file called `members/<your-github-username>.md`
3. Write in it your name, your year or major, and your favorite team or sport
4. Commit it, push it to your fork, and open a pull request to the club repo

**Done when:** your pull request is open on GitHub.

**Challenge**

Open a pull request for your `top_rebounders.sql` from Take-home 1. Fill in the pull request template, and move your card to "Done" on the board when it's merged.

<details>
<summary>Stuck?</summary>

- "Permission denied" when pushing? Make sure you push to `origin` (your fork), not `upstream`.
- Not sure your pull request went to the right place? It should say `base: data-science-ucsb/main`.
- Step-by-step Git help is in [CONTRIBUTING.md](CONTRIBUTING.md).
</details>

---

## Workshop 3: Data Analytics (10/27, Diego)

**In the workshop:** combine tables with `JOIN`, use `CASE WHEN` to make decisions inside a query (like "was this a win or a loss?"), and turn the results into charts.

**By the end you will have:**
- Written a query that joins two or more tables
- Understood how the ID columns connect the tables (see [The data](README.md#the-data) in the README)
- Made a chart from a query result

### Take-home 3: Build the Player Profile query

**How the workshop helps:** a player's game log needs four tables. `JOIN` connects them, and `CASE WHEN` works out who the opponent was.

**Starter**

1. Open `sql/player_profile.sql` and read the hints at the top
2. Write the query below the hints
3. Run `pytest`. The `test_player_profile` test will stop skipping and start checking your work.

**Done when:** `pytest` passes, and the Player Profile page shows a table when you type in a player's name.

**Challenge**

Do one of these:
- Add a line chart of points over time to the Player Profile page. Replace the `TODO` comment in `app/pages/4_Player_Profile.py` with `px.line`, copying how `1_Top_Scorers.py` draws its chart.
- Write `sql/team_standings.sql` (hints inside). It's harder because every game involves two teams. The hints show a trick for handling that.

<details>
<summary>Stuck?</summary>

- Start small. Join just `player_game_stats` and `players` and check that the output looks right, then add one table at a time.
- To find a player's name to test with, run `SELECT name FROM players LIMIT 5;`
- If you get way too many rows, a `JOIN ... ON` condition is probably missing or wrong.
</details>

---

## Workshop 4: Classical ML (11/2, Jakob)

**In the workshop:** classical machine learning with scikit-learn. Grouping similar things together (clustering, the same idea marketers use to sort customers into segments), and predicting outcomes from data.

**By the end you will have:**
- Trained a model in Python with scikit-learn
- Understood the difference between grouping data (clustering) and predicting an answer (classification)

### Take-home 4: Group players into "player types"

Marketers group customers into segments like "bargain hunters" and "big spenders". You will do the same with players: scorers, rebounders, playmakers, and bench players.

**How the workshop helps:** this is customer segmentation, with players instead of customers. Each player's per-game points, rebounds, and assists are their "features", and k-means clustering finds the groups.

**Starter**

1. Write a query, `sql/player_averages.sql`, that returns each player's average points, rebounds, and assists per game. It looks a lot like `top_scorers.sql`.
2. In a new Python file or notebook, load it with `run_query("player_averages")`
3. Use `KMeans(n_clusters=4)` from scikit-learn to group the players
4. Look at each group. Can you give it a name?

**Done when:** every player has a group, and you can describe what each group has in common.

**Challenge**

- Turn it into a dashboard page: a scatter plot of points vs. rebounds, colored by group (copy `1_Top_Scorers.py`)
- Or predict games: use `LogisticRegression` to guess whether the home team wins, from each team's average points

<details>
<summary>Stuck?</summary>

- scikit-learn is already in `requirements.txt`. If `import sklearn` fails, run `pip install -r requirements.txt` again.
- Clustering works better when every column is on the same scale. Look up `StandardScaler`.
- Not sure how many groups to use? Try 3, 4, and 5, and see which groups make the most sense.
</details>

---

## Workshop 5: Deployment (11/9, Clement)

**In the workshop:** put the dashboard online with Streamlit Community Cloud (free), so anyone can open it with a link.

**By the end you will have:**
- A public link to the club's dashboard that you can share with anyone

### Take-home 5: Deploy your own copy

Your fork is your own version of the project, and you can put it online too. That gives you a link to show people.

**Starter**

1. Sign in at [streamlit.io/cloud](https://streamlit.io/cloud) with GitHub
2. Click **New app** and choose *your fork*, branch `main`, main file `app/Home.py`
3. The app builds its database automatically the first time it loads

**Done when:** you can open your dashboard on your phone.

**Challenge**

Add a page that answers a question of your own, so your deployed copy has something nobody else's does:
1. Write the SQL in a new file in `sql/`
2. Make a new page in `app/pages/` by copying an existing page
3. Push it to your fork. Your deployed app updates automatically.

Question ideas:
- **Home-court advantage:** do teams really win more at home?
- **Head-to-head:** pick two teams and show every game between them
- **Compare two players:** show their stats side by side
- **Close games:** write `sql/close_games.sql` (hints inside) and add a chart
- **Hot streaks:** find each team's longest winning streak (look up SQL "window functions")
- **Is "clutch" real?** Compare each team's close-game win percentage with its overall win percentage

<details>
<summary>Stuck?</summary>

- App won't start? Click **Manage app** in the bottom corner to see the error log.
- Changes not showing up? Make sure you pushed to your fork's `main` branch.
</details>

---

## Workshop 6: How to Talk About Your Project (11/16, Sid)

**In the workshop:** explain what you built, why it matters, and what you learned, for a resume, an interview, or a demo.

**By the end you will have:**
- A short pitch for this project that you can say out loud

### Take-home 6: Write your project pitch

**How the workshop helps:** you already built the thing. This is about turning it into a story: the question, what you did, and what you found.

**Starter**

Add a "My work" section to your `members/<your-github-username>.md` file from Take-home 2, with:
1. One sentence on what the project is
2. What you built (for example "the Player Profile page" or "player-type clustering")
3. One interesting thing the data showed
4. The link to your deployed dashboard from Take-home 5

Open a pull request with it.

**Done when:** a friend who doesn't code can read it and understand what you did.

**Challenge**

- Write a resume bullet for this project. Start with an action verb and include a number, like "Built a SQL and Python dashboard analyzing 1,000+ player game records."
- Record a 60-second demo of your dashboard and practice explaining it.

---

## After the workshops

These are bigger group projects for anyone who wants to keep going. You don't need to look at them until the workshops are done.

<details>
<summary>Use real data instead of the fake league</summary>

1. As a group, choose a league. Some options:
   - NBA, using the [`nba_api`](https://github.com/swar/nba_api) Python package
   - Datasets on [Kaggle](https://www.kaggle.com/datasets?search=basketball)
   - Soccer results from [football-data.co.uk](https://www.football-data.co.uk/data.php)
   - Anything else the group cares about
2. Write `scripts/fetch_real_data.py` to download the data and save it as CSV files in the same shape as `data/raw/` (see `data/README.md`)
3. Add useful extra columns to `db/schema.sql`, like three-pointers or fouls
4. Update the tests that assume there are 8 teams
</details>

<details>
<summary>Polish the dashboard</summary>

- Use the same colors on every page
- Add team logos
- Write a better home page that explains what each page answers
</details>

---

## Tips for working together

- **Say what you're working on** by claiming a card on the project board (or a GitHub issue), so two people don't build the same page.
- **Pull before you start:** `git pull upstream main`. That way you're building on everyone's latest work.
- **Keep pull requests small.** One task per pull request gets reviewed faster.
- **Take-homes are practice.** Leads will merge one working version of each task and give feedback on the rest. Your work counts either way.
- **Ask for help early.** If you've been stuck for 20 minutes, post your error in the channel.

Have an idea that isn't here? Open an issue with the **Task** template, or bring it to the next workshop.
