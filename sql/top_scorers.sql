-- =============================================================
-- Top scorers  ✅ WORKED EXAMPLE -- use this as a template!
--
-- Question: Who scores the most points per game?
--
-- Concepts:  JOIN (3 tables), GROUP BY, aggregate functions
--            (COUNT, SUM, AVG), HAVING, ORDER BY, LIMIT
--
-- Params:    :limit       how many players to return
--            :min_games   ignore players with fewer games than this
--
-- Returns:   player, team, games, total_points, points_per_game
-- =============================================================

SELECT
    p.name                          AS player,
    t.abbreviation                  AS team,
    COUNT(*)                        AS games,
    SUM(s.points)                   AS total_points,
    ROUND(AVG(s.points), 1)         AS points_per_game
FROM player_game_stats AS s
JOIN players AS p ON p.player_id = s.player_id
JOIN teams   AS t ON t.team_id   = s.team_id
GROUP BY p.player_id
HAVING COUNT(*) >= :min_games
ORDER BY points_per_game DESC
LIMIT :limit;
