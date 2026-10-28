---
name: "Take-home 4: Player types"
about: Your own card for the Workshop 4 take-home. Nothing to fill in, just click Create.
title: "[Take-home 4] Player types"
labels: ["take-home", "workshop-4"]
---

<!-- You don't need to change anything here. Scroll down and click "Create". -->

This is my card for **Take-home 4**. Full instructions and hints: [ROADMAP.md](https://github.com/data-science-ucsb/sports-stats-explorer/blob/main/ROADMAP.md#take-home-4-group-players-into-player-types)

## Steps
- [ ] Write `sql/player_averages.sql`: each player's average points, rebounds, and assists per game
- [ ] Load it in a new Python file or notebook with `run_query("player_averages")`
- [ ] Group the players with `KMeans(n_clusters=4)` from scikit-learn
- [ ] Look at each group and give it a name

## Done when
Every player has a group, and I can describe what each group has in common.

## When I'm finished
- **Want feedback?** Open a pull request with `Closes #<this card's number>` in the description. The card moves along by itself.
- **No pull request?** Click **Close issue** at the bottom of this page.

**Challenge (optional):** use `LogisticRegression` to guess whether the home team wins, from each team's average points. Or turn your groups into a dashboard page: that's the **Add a Player Types page** card on the [Club tasks board](https://github.com/orgs/data-science-ucsb/projects/11).
