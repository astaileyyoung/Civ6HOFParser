CREATE TABLE `DataSets` (
  `hof_id` INT NOT NULL,
  `DataSetId` bigint NOT NULL,
  `DataSet` text,
  `Ruleset` text,
  `GameId` text,
  `ObjectId` bigint DEFAULT NULL,
  `Type` text,
  PRIMARY KEY (hof_id, DataSetId)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;