FROM grafana/grafana-oss

COPY ./dashboards/ /var/lib/grafana/dashboards/
COPY ./dashboard.yaml /etc/grafana/provisioning/dashboards/dashboard.yaml
COPY ./datasource.yaml /etc/grafana/provisioning/datasources/datasource.yaml

# open port
EXPOSE 3000
