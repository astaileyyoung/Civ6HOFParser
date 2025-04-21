CREATE TABLE `GamePlayers` (
  `hof_id` INT NOT NULL,
  `PlayerObjectId` bigint NOT NULL,
  `IsLocal` bigint DEFAULT NULL,
  `IsAI` bigint DEFAULT NULL,
  `IsMajor` bigint DEFAULT NULL,
  `LeaderType` text,
  `LeaderName` text,
  `CivilizationType` text,
  `CivilizationName` text,
  `DifficultyType` text,
  `Score` bigint DEFAULT NULL,
  `PlayerId` bigint DEFAULT NULL,
  `TeamId` bigint DEFAULT NULL,
  PRIMARY KEY (`hof_id`, `PlayerObjectId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;