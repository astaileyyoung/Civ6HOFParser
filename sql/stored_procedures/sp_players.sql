CREATE PROCEDURE PlayerUpdate()
BEGIN
    DECLARE i INT;
    DECLARE player_id INT;
    DECLARE game_id INT;
    DECLARE cnt INT;
    DECLARE is_new_game INT;

    CREATE TEMPORARY TABLE IF NOT EXISTS Players (
        IDX                     INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        PlayerObjectId          INT,
        IsLocal                 INT,
        IsAI                    INT,
        IsMajor                 INT,
        LeaderName              VARCHAR(255),
        CivilizationName        VARCHAR(255),
        DifficultyType          VARCHAR(255),
        PlayerId                INT,
        TeamId                  INT,
        GameId                  INT
    );

    TRUNCATE TABLE Players;
    
    INSERT INTO Players (`PlayerObjectId`, `IsLocal`, `IsAI`, `IsMajor`, `LeaderName`, `CivilizationName`, `DifficultyType`, `PlayerId`, `TeamId`)
    SELECT 
        PlayerObjectId,
        IsLocal,
        IsAI,
        IsMajor,
        LeaderName,
        `CivilizationName`,
        `DifficultyType`,
        `PlayerId`,
        `TeamId`
    FROM `GamePlayers`;

    SET i = 1;
    SET cnt = (SELECT COUNT(*) FROM `GamePlayers`);
    SET game_id = 0;
    SET is_new_game = 0;

    WHILE i <= cnt DO
        SET player_id = (SELECT `PlayerObjectId` FROM Players WHERE IDX = i);

        SET is_new_game = (SELECT CASE 
                                       WHEN (SELECT IsLocal FROM GamePlayers WHERE `PlayerObjectId` = player_id) = 1 THEN 1 ELSE 0
                                   END
                            FROM DUAL);

        SET game_id = (SELECT CASE WHEN is_new_game = 1 THEN game_id + 1 ELSE game_id END FROM DUAL);
    
        UPDATE Players  
        SET GameId = game_id
        WHERE PlayerObjectId = player_id;
        
        SET i = i + 1;
            
    END WHILE;

    SELECT * FROM Players;

    CREATE TABLE IF NOT EXISTS civDW.Players (
        PlayerObjectId          INT,
        IsLocal                 INT,
        IsAI                    INT,
        IsMajor                 INT,
        LeaderName              VARCHAR(255),
        CivilizationName        VARCHAR(255),
        DifficultyType          VARCHAR(255),
        PlayerId                INT,
        TeamId                  INT,
        GameId                  INT
    );

    TRUNCATE TABLE civDW.Players;

    ALTER TABLE Players DROP COLUMN IDX;

    INSERT INTO civDW.Players
    SELECT * FROM Players;
    
    DROP TEMPORARY TABLE Players;

END;