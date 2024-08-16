-- Does not include city state data. I'm not 100% sure, but it seems like the city state data is not included in the same tables.
-- However, I really need to make sure there is no problem with my query.

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
WHERE ds.`DataSet` IS NOT NULL
