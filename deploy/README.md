# Capstone Monitoring Stack (Prometheus + InfluxDB v2 + Telegraf + Grafana)

This stack stores all configs and persistent data under:

/home/alpha/Capstone/Docker

---

## Create folder structure (everything lives here)

sudo mkdir -p /home/alpha/Capstone/Docker/prometheus/data
sudo mkdir -p /home/alpha/Capstone/Docker/telegraf
sudo mkdir -p /home/alpha/Capstone/Docker/grafana/data
sudo mkdir -p /home/alpha/Capstone/Docker/grafana/provisioning
sudo mkdir -p /home/alpha/Capstone/Docker/influxdb/data
sudo mkdir -p /home/alpha/Capstone/Docker/influxdb/config

---

## Create Prometheus config

File: /home/alpha/Capstone/Docker/prometheus/prometheus.yml

sudo tee /home/alpha/Capstone/Docker/prometheus/prometheus.yml >/dev/null <<'YAML'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]
YAML

---

## Create Telegraf config (writes host metrics to InfluxDB v2)

File: /home/alpha/Capstone/Docker/telegraf/telegraf.conf

sudo tee /home/alpha/Capstone/Docker/telegraf/telegraf.conf >/dev/null <<'CONF'
[agent]
  interval = "10s"
  round_interval = true
  metric_batch_size = 1000
  metric_buffer_limit = 10000
  flush_interval = "10s"

[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "admintoken=="
  organization = "microgrid"
  bucket = "telemetry"

[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false
  report_active = true

[[inputs.mem]]

[[inputs.disk]]
  ignore_fs = ["tmpfs", "devtmpfs", "overlay", "squashfs"]
CONF

---

## Set permissions for persistent data directories

sudo chown -R 65534:65534 /home/alpha/Capstone/Docker/prometheus/data
sudo chown -R 472:472 /home/alpha/Capstone/Docker/grafana/data
sudo chown -R 1000:1000 /home/alpha/Capstone/Docker/influxdb/data /home/alpha/Capstone/Docker/influxdb/config || true

---

## Create docker-compose.yml (final working version)

File: /home/alpha/Capstone/Docker/docker-compose.yml

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - /home/alpha/Capstone/Docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - /home/alpha/Capstone/Docker/prometheus/data:/prometheus
    restart: unless-stopped

  influxdb:
    image: influxdb:2
    container_name: influxdb
    ports:
      - "8086:8086"
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: admin
      DOCKER_INFLUXDB_INIT_PASSWORD: adminpass
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: "admintoken=="
      DOCKER_INFLUXDB_INIT_ORG: microgrid
      DOCKER_INFLUXDB_INIT_BUCKET: telemetry
    volumes:
      - /home/alpha/Capstone/Docker/influxdb/data:/var/lib/influxdb2
      - /home/alpha/Capstone/Docker/influxdb/config:/etc/influxdb2
    restart: unless-stopped

  telegraf:
    image: telegraf:latest
    container_name: telegraf
    depends_on:
      - influxdb
    volumes:
      - /home/alpha/Capstone/Docker/telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
      - influxdb
    environment:
      GF_SECURITY_ADMIN_PASSWORD: grafana
    volumes:
      - /home/alpha/Capstone/Docker/grafana/provisioning:/etc/grafana/provisioning:ro
      - /home/alpha/Capstone/Docker/grafana/data:/var/lib/grafana
    restart: unless-stopped

---

## Deployments (start/stop/delete)

cd /home/alpha/Capstone/Docker

docker compose up -d
docker compose ps
docker compose logs -f

docker compose logs -f prometheus
docker compose logs -f influxdb
docker compose logs -f telegraf
docker compose logs -f grafana

docker compose stop
docker compose down
docker compose down -v

---

## Service access and credentials

Prometheus
- http://localhost:9090

InfluxDB (v2)
- http://localhost:8086
- username: admin
- password: adminpass
- org: microgrid
- bucket: telemetry
- token: admintoken==

Telegraf
- no web UI
- writes to InfluxDB org microgrid bucket telemetry

Grafana
- http://localhost:3000
- user: admin
- pw: grafana

Provisioning path (datasources/dashboards):
/home/alpha/Capstone/Docker/grafana/provisioning

Restart Grafana after provisioning changes:
docker compose restart grafana
docker compose logs --tail=200 grafana

---

## Ports summary
- Prometheus: 9090
- InfluxDB: 8086
- Grafana: 3000
- Telegraf: none

If accessing from another machine, replace localhost with your server IP (example: http://10.26.0.71:3000)
