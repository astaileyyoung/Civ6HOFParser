DELIMITER //

CREATE PROCEDURE civDW.completed_techs()
BEGIN 

    CREATE TABLE IF NOT EXISTS CompletedTechs (
        game_id VARCHAR(255),
        player_id INT,
        civilization VARCHAR(255),
        leader VARCHAR(255),
        turn INT,
        tech VARCHAR(255),
        completed INT,
        PRIMARY KEY (game_id, player_id, tech, completed)
    );
    TRUNCATE TABLE CompletedTechs;

    INSERT INTO CompletedTechs (game_id, player_id, civilization, leader, tech, turn, completed)
    SELECT 
        techs.game_id,
        techs.player_id,
        players.civilization,
        players.leader,
        techs.tech,
        techs.turn,
        CASE 
            WHEN techs.turns <= 1 THEN 1 ELSE 0
        END AS completed
    FROM (
        SELECT 
            game_id,
            player_id,
            tech,
            MAX(turn) AS turn,
            MIN(turns) AS turns
        FROM civLOG.Research 
        GROUP BY game_id, player_id, tech
    ) AS techs
    LEFT JOIN civLOG.Players AS players ON techs.game_id = players.game_id AND techs.player_id = players.player_id;

END //

DELIMITER ;