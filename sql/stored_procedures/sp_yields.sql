CREATE PROCEDURE civDW.update_yields()
BEGIN 

    DROP TABLE IF EXISTS civDW.Yields;

    CREATE TABLE IF NOT EXISTS civDW.Yields (
        hof_id          INT,
        ObjectId        INT,
        GameId          INT,
        PlayerObjectId  INT,
        IsLocal         TINYINT,
        IsAI            TINYINT,
        Type            VARCHAR(255),
        Name            VARCHAR(255),
        DataSetId       INT,
        DataSet         VARCHAR(255),
        Turn            INT,
        Value           INT,
        Civilization    VARCHAR(255),
        Leader          VARCHAR(255),
        PRIMARY KEY (hof_id, ObjectId, GameId, PlayerObjectId, DataSet, Turn)
    );

    INSERT INTO civDW.Yields (
        `hof_id`,
        `ObjectId`,
        `GameId`, 
        `PlayerObjectId`, 
        `IsLocal`,
        `IsAI`,
        `Type`, 
        `Name`, 
        `DataSetId`, 
        `DataSet`, 
        `Turn`, 
        `Value`, 
        `Civilization`,
        `Leader`)
    SELECT 
        gob.hof_id,
        gob.`ObjectId`,
        gob.`GameId`,
        COALESCE(gob.`PlayerObjectId`, gob.`ObjectId`) AS `PlayerObjectId`,
        gp.`IsLocal`,
        gp.`IsAI`,
        gob.Type,
        gob.Name,
        ds.`DataSetId`,
        ds.`DataSet`,
        dsv.X AS Turn,
        dsv.Y AS Value,
        gp.`CivilizationName` AS Civilization,
        gp.`LeaderName` As Leader
    FROM (
        SELECT 
            `hof_id`,
            `ObjectId`,
            `GameId`,
            COALESCE(`PlayerObjectId`, `ObjectId`) AS `PlayerObjectId`,
            `Type`,
            `Name`
        FROM civ.`GameObjects`
    ) gob
    LEFT JOIN civ.`GamePlayers` AS gp ON
        gob.`PlayerObjectId` = gp.`PlayerObjectId`
        AND gob.hof_id = gp.hof_id
    LEFT JOIN civ.`DataSets` AS ds ON
        gob.`ObjectId` = ds.`ObjectId`
        AND gob.hof_id = ds.hof_id
    LEFT JOIN civ.`DataSetValues` AS dsv ON
        ds.`DataSetId` = dsv.`DataSetId`
        AND gob.hof_id = dsv.hof_id
    WHERE ds.`DataSet` IS NOT NULL;

END;