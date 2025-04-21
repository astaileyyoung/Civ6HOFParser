CREATE TABLE `DataSetValues` (
  `hof_id` INT NOT NULL,
  `DataSetId` bigint,
  `X` bigint,
  `Y` double DEFAULT NULL,
  PRIMARY KEY (hof_id, DataSetId, X)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;