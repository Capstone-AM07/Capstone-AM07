# Deployments

```bash
# start/create deployment
docker compose up

# stop deployment
docker compose stop

# delete deployment
docker compose down
```

## Prometheus

## InfluxDB

## Telegraf

## Grafana

[http://localhost:3000](http://localhost:3000)
- user: admin
- pw: grafana

Connections to InfluxDB and Prometheus are automatically created as defined in `grafana/provisioning/datasources/datasources.yml`
