-- Active: 1719696896858@@192.168.0.131@3306@civ
SELECT * FROM Games

SELECT * FROM GamePlayers 

SELECT * FROM DataSets

SELECT DISTINCT(ObjectId) FROM DataSets 

SELECT * FROM DataSetValues

SELECT * FROM DataSetValues

SELECT 
    CASE 
        WHEN (SELECT IsLocal FROM GamePlayers WHERE `PlayerObjectId` = 2) = 1 THEN 1 ELSE 0
    END 
FROM DUAL;

CALL civDW.update_yields

DROP PROCEDURE civDW.update_yields;

DROP TEMPORARY TABLE Players

SELECT * FROM civDW.`Players`


SELECT 
    civDW.Players.*,
    civ.DataSets.`DataSet`,
    civ.DataSetValues.
FROM civDW.`Players`
INNER JOIN civ.DataSets
    ON civDW.Players.`PlayerObjectId` = civ.DataSets.ObjectId
INNER JOIN civ.DataSetValues 
    ON civ.DataSetValues.`DataSetId` = civ.DataSets.`DataSetId`


SELECT 
    PLAYERS.`PlayerObjectId`,
    `PLAYERS`.`CivilizationName`,
    `PLAYERS`.`LeaderName`,
    `PLAYERS`.`GameId`,
    c.`DataSet`,
    c.`DataSetId`,
    c.`ObjectId`,
    c.X,
    c.Y
FROM civDW.`Players` AS PLAYERS
INNER JOIN (
    SELECT 
        b.*,
        a.`DataSet`,
        a.`ObjectId`
    FROM civ.`DataSets` AS a
    INNER JOIN civ.`DataSetValues` AS b 
        ON a.`DataSetId` = b.`DataSetId`
) c
ON c.`ObjectId` = PLAYERS.`PlayerObjectId`


INNER JOIN civ.`DataSets` AS DATASETS
    ON PLAYERS.`PlayerObjectId` = DATASETS.`ObjectId`
INNER JOIN civ.`DataSetValues` AS VALUES 
    ON DATASETS.`DataSetId` = VALUES.`DataSetId`


SELECT 
    a.*,
    go.name,
    dsv.*
FROM (
    SELECT * 
    FROM `DataSets`
    WHERE `ObjectId` = 30
) a 
LEFT JOIN `DataSetValues` AS dsv ON 
    a.DataSetId = dsv.`DataSetId`
LEFT JOIN `GameObjects` AS go ON 
    a.ObjectId = go.`ObjectId`


SELECT 
    dsv.*,
    ds.DataSet,
    ds.`ObjectId`,
    go.Name,
    go.Type,
    gp.`CivilizationName`,
    gp.`LeaderName`,
    p.`GameId`
FROM `DataSetValues` AS dsv
INNER JOIN `DataSets` ds ON
    dsv.`DataSetId` = ds.`DataSetId`
INNER JOIN `GameObjects` AS go ON
    ds.`ObjectId` = go.`ObjectId`
LEFT JOIN `GamePlayers` AS gp ON 
    go.`PlayerObjectId` = gp.`PlayerObjectId`
LEFT JOIN civDW.`Players` AS p ON
    go.`PlayerObjectId` = p.`PlayerObjectId`
WHERE go.Name IS not NULL


SELECT 
    go.`ObjectId`,
    go.`GameId`,
    COALESCE(go.`PlayerObjectId`, go.`ObjectId`) AS `PlayerObjectId`,
    go.Type,
    go.Name,
    ds.`DataSetId`,
    ds.`DataSet`,
    dsv.X,
    dsv.Y,
    gp.`CivilizationName`,
    gp.`LeaderName`
FROM (
    SELECT 
        `ObjectId`,
        `GameId`,
        COALESCE(`PlayerObjectId`, `ObjectId`) AS `PlayerObjectId`,
        `Type`,
        `Name`
    FROM `GameObjects`
) go
LEFT JOIN `GamePlayers` AS gp ON
    go.`PlayerObjectId` = gp.`PlayerObjectId`
LEFT JOIN `DataSets` AS ds ON
    go.`ObjectId` = ds.`ObjectId`
LEFT JOIN `DataSetValues` AS dsv ON
    ds.`DataSetId` = dsv.`DataSetId`

-- WHERE go.Name IS NOT NULL
SELECT * 
FROM `GameObjects`
