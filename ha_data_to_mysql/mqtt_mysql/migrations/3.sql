CREATE TABLE `ha_entities` (`entity` varchar(255) NOT NULL,`friendly_name` varchar(255) NOT NULL,`entity_type` varchar(255) NOT NULL,`entity_name` varchar(255) NOT NULL,UNIQUE KEY `entity` (`entity`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
ALTER TABLE `ha_entities` ADD CONSTRAINT PK_ha_entities PRIMARY KEY (`entity`);
insert into mqtt_data.ha_entities (entity,friendly_name,entity_type,entity_name)
select distinct entity, friendly_name, SUBSTRING_INDEX(entity, '.', 1), SUBSTRING_INDEX(entity, '.', 2) from mqtt_data.ha_state_change;
UPDATE schema_version set validity = 0 where validity = 1;
INSERT INTO schema_version (version, validity) VALUES (3, 1);
