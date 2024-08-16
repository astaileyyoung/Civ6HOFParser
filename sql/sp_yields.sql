CREATE PROCEDURE civDW.update_yields()
BEGIN 

    CREATE TABLE IF NOT EXISTS civDW.Yields (
        ObjectId        INT,
        GameId          INT,
        PlayerObjectId  INT,
        Type            VARCHAR(255),
        Name            VARCHAR(255),
        DataSetId       INT,
        DataSet         VARCHAR(255),
        Turn            INT,
        Value           INT,
        Civilization    VARCHAR(255),
        Leader          VARCHAR(255),
        PRIMARY KEY (ObjectId, GameId, PlayerObjectId, DataSet, Turn)
    );
    TRUNCATE TABLE civDW.Yields;

    INSERT INTO civDW.Yields (
        `ObjectId`,
        `GameId`, 
        `PlayerObjectId`, 
        `Type`, 
        `Name`, 
        `DataSetId`, 
        `DataSet`, 
        `Turn`, 
        `Value`, 
        `Civilization`,
        `Leader`)
    SELECT 
        go.`ObjectId`,
        go.`GameId`,
        COALESCE(go.`PlayerObjectId`, go.`ObjectId`) AS `PlayerObjectId`,
        go.Type,
        go.Name,
        ds.`DataSetId`,
        ds.`DataSet`,
        dsv.X AS Turn,
        dsv.Y AS Value,
        gp.`CivilizationName` AS Civilization,
        gp.`LeaderName` As Leader
    FROM (
        SELECT 
            `ObjectId`,
            `GameId`,
            COALESCE(`PlayerObjectId`, `ObjectId`) AS `PlayerObjectId`,
            `Type`,
            `Name`
        FROM civ.`GameObjects`
    ) go
    LEFT JOIN civ.`GamePlayers` AS gp ON
        go.`PlayerObjectId` = gp.`PlayerObjectId`
    LEFT JOIN civ.`DataSets` AS ds ON
        go.`ObjectId` = ds.`ObjectId`
    LEFT JOIN civ.`DataSetValues` AS dsv ON
        ds.`DataSetId` = dsv.`DataSetId`
    WHERE ds.`DataSet` IS NOT NULL;

END;