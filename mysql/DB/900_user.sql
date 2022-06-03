DROP USER IF EXISTS 'grafana';
CREATE USER 'grafana' identified by 'grafana';

GRANT SELECT ON `tod`.* TO 'grafana';


DROP USER IF EXISTS 'tod-logic';
CREATE USER 'tod-logic' identified by 'h4UFhn3AGYAVc6hRxdsSWVbwSxMxfZPpsETXS7ZPA8LRkPANeKNFCAvXTexcZqTe';

GRANT INSERT, SELECT, UPDATE, DELETE ON `tod`.* TO 'tod-logic';
