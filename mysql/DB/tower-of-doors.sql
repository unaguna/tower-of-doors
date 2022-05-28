SET @old_autocommit=@@autocommit;

--
-- Current Database: `tod`
--

DROP DATABASE IF EXISTS `tod`;

CREATE DATABASE `tod` DEFAULT CHARACTER SET utf8mb4;

USE `tod`;

--
-- Table structure for table `door`
--

DROP TABLE IF EXISTS `door`;
CREATE TABLE `door` (
  `id` char(8) NOT NULL,
  # Floor on which the question is written
  # 1: the ground floor
  `floor` int NOT NULL,
  # link code
  # 1: to outside
  # 0: to lower floor
  # -1: to inside
  `link_code` int NOT NULL,
  # azimuth id
  # NULL: if this door is on the floor
  # 0-5: if this door is on the wall
  `azimuth_id` int,
  # Vertical travel distance (by floor number)
  # 0: if this door is not on the floor
  `vertical_move` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `door`
--

set autocommit=0;
INSERT INTO `door` (`id`, `floor`, `link_code`, `azimuth_id`, `vertical_move`) VALUES
  ('F5-I-000', 5, -1, 0, 0),
  ('F5-I-060', 5, -1, 1, 0),
  ('F5-I-120', 5, -1, 2, 0),
  ('F5-I-180', 5, -1, 3, 0),
  ('F5-I-240', 5, -1, 4, 0),
  ('F5-I-300', 5, -1, 5, 0),
  ('F5-O-000', 5, 1, 0, 0),
  ('F5-O-060', 5, 1, 1, 0),
  ('F5-O-120', 5, 1, 2, 0),
  ('F5-O-180', 5, 1, 3, 0),
  ('F5-O-240', 5, 1, 4, 0),
  ('F5-O-300', 5, 1, 5, 0),
  ('F4-O-000', 4, 1, 0, 0),
  ('F4-O-060', 4, 1, 1, 0),
  ('F4-O-120', 4, 1, 2, 0),
  ('F4-O-180', 4, 1, 3, 0),
  ('F4-O-240', 4, 1, 4, 0),
  ('F4-O-300', 4, 1, 5, 0),
  ('F3-O-000', 3, 1, 0, 0),
  ('F3-O-060', 3, 1, 1, 0),
  ('F3-O-120', 3, 1, 2, 0),
  ('F3-O-180', 3, 1, 3, 0),
  ('F3-O-240', 3, 1, 4, 0),
  ('F3-O-300', 3, 1, 5, 0),
  ('F2-O-000', 2, 1, 0, 0),
  ('F2-O-060', 2, 1, 1, 0),
  ('F2-O-120', 2, 1, 2, 0),
  ('F2-O-180', 2, 1, 3, 0),
  ('F2-O-240', 2, 1, 4, 0),
  ('F2-O-300', 2, 1, 5, 0),
  ('F1-I-000', 1, -1, 0, 0),
  ('F1-I-060', 1, -1, 1, 0),
  ('F1-I-120', 1, -1, 2, 0),
  ('F1-I-180', 1, -1, 3, 0),
  ('F1-I-240', 1, -1, 4, 0),
  ('F1-I-300', 1, -1, 5, 0),
  ('F1-O-000', 1, 1, 0, 0),
  ('F1-O-060', 1, 1, 1, 0),
  ('F1-O-120', 1, 1, 2, 0),
  ('F1-O-180', 1, 1, 3, 0),
  ('F1-O-240', 1, 1, 4, 0),
  ('F1-O-300', 1, 1, 5, 0),

  ('F5F4-001', 5, 0, NULL, 1),
  ('F5F3-001', 5, 0, NULL, 2),
  ('F4F3-001', 4, 0, NULL, 1),
  ('F4F2-001', 4, 0, NULL, 2),
  ('F3F2-001', 3, 0, NULL, 1),
  ('F3F1-001', 3, 0, NULL, 2),
  ('F2F1-001', 2, 0, NULL, 1)
;

--
-- Table structure for table `azimuth_log`
--

DROP TABLE IF EXISTS `azimuth_log`;
CREATE TABLE `azimuth_log` (
  `azimuth` double NOT NULL,
  `timestamp` datetime NOT NULL,
  `yawing` boolean NOT NULL,
  PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Data for table `azimuth_log`
--

set autocommit=0;
INSERT INTO `azimuth_log` (`azimuth`, `timestamp`, `yawing`) VALUES
  (0.0, now(), false)
;


--
-- Table structure for table `door_log_reason`
--

DROP TABLE IF EXISTS `door_log_reason`;
CREATE TABLE `door_log_reason` (
  # reason of status
  # 'GAME_PHASE': Close due to the end of the answer time
  # 'ANSWER': Open by correct answer
  # 'REMOTE': Open or close by remote control
  # 'MASTER_KEY': Open or close by the card key
  `reason` char(10) NOT NULL,
  PRIMARY KEY (`reason`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Data for table `door_log_reason`
--

set autocommit=0;
INSERT INTO `door_log_reason` (`reason`) VALUES
  ('GAME_PHASE'),
  ('ANSWER'),
  ('REMOTE'),
  ('MASTER_KEY')
;


--
-- Table structure for table `door_log`
--

DROP TABLE IF EXISTS `door_log`;
CREATE TABLE `door_log` (
  `door_id` char(8) NOT NULL,
  # Door status
  # 0: close
  # 1: open
  `status` tinyint unsigned NOT NULL,
  `timestamp` datetime NOT NULL,
  # reason of status
  `reason` char(10) NOT NULL,
  PRIMARY KEY (`door_id`, `timestamp`),
  FOREIGN KEY fk_door_log(`door_id`) REFERENCES `door`(`id`),
  FOREIGN KEY fk_door_log_reason(`reason`) REFERENCES `door_log_reason`(`reason`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- View `door_status`
--

CREATE VIEW door_status
AS SELECT
  door.id,
  door_log.status,
  door_log.reason,
  door_log.`timestamp`
FROM door
LEFT JOIN door_log ON door_log.door_id = door.id
INNER JOIN (
  SELECT
    door.id,
    max(door_log.`timestamp`) as `time`
  FROM door
  LEFT JOIN door_log ON door_log.door_id = door.id
  GROUP BY door.id
) AS `sub` ON door.id = `sub`.id and (door_log.`timestamp` = `sub`.`time` or door_log.`timestamp` is null)
;

SET autocommit=@old_autocommit;
