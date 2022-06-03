DROP USER IF EXISTS 'grafana';
CREATE USER 'grafana' identified by 'grafana';

GRANT SELECT ON `tod`.* TO 'grafana';
