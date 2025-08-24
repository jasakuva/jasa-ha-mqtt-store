CREATE TABLE `test` (`test` varchar(255)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
UPDATE schema_version set validity = 0 where validity = 1;
INSERT INTO schema_version (version, validity) VALUES (4, 1);
