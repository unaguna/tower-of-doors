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
  `down_level` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Data for table `door`
--

set autocommit=0;
INSERT INTO `door` (`id`, `floor`, `link_code`, `azimuth_id`, `down_level`) VALUES
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

  ('F5F4-001', 5, 0, NULL, 1),
  ('F5F3-001', 5, 0, NULL, 2)
;
commit;

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
-- Table structure for table `door_log`
--

DROP TABLE IF EXISTS `door_log`;
CREATE TABLE `door_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `door_id` char(8) NOT NULL,
  # Door status
  # 0: close
  # 1: open
  `status` tinyint unsigned NOT NULL,
  `timestamp` datetime NOT NULL,
  # reason of status
  # 'GAME_PHASE': Due to the end of the answer time
  # 'MANUAL'
  `reason` char(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


SET autocommit=@old_autocommit;
