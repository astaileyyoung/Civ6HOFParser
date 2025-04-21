-- Active: 1719696896858@@192.168.0.131@3306@civ
-- Active: 1719696896858@@192.168.0.131@3306@civDW
-- Does not include city state data. I'm not 100% sure, but it seems like the city state data is not included in the same tables.
-- However, I really need to make sure there is no problem with my query.

SELECT 
    gob.`ObjectId`,
    gob.`GameId`,
    COALESCE(gob.`PlayerObjectId`, gob.`ObjectId`) AS `PlayerObjectId`,
    gob.Type,
    gob.Name,
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
) AS gob
LEFT JOIN `GamePlayers` AS gp ON
    gob.`PlayerObjectId` = gp.`PlayerObjectId`
LEFT JOIN `DataSets` AS ds ON
    gob.`ObjectId` = ds.`ObjectId`
LEFT JOIN `DataSetValues` AS dsv ON
    ds.`DataSetId` = dsv.`DataSetId`
WHERE ds.`DataSet` IS NOT NULL
