CREATE TABLE `GameObjects` (
  `hof_id` INT NOT NULL,
  `ObjectId` bigint NOT NULL,
  `GameId` bigint DEFAULT NULL,
  `PlayerObjectId` double DEFAULT NULL,
  `Type` text,
  `Name` text,
  `PlotIndex` double DEFAULT NULL,
  `ExtraData` text,
  `Icon` text,
  PRIMARY KEY (hof_id, ObjectId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;