# Raspberry Pi Weather Station Node (Sensors -> VM1)
# Capstone Telemetry Pipeline (Raspberry Pi Sensors → InfluxDB → Grafana)

This setup reads I2C sensors on a Raspberry Pi (BME280 + VEML7700) and pushes the data to an InfluxDB v2 instance running on an Ubuntu VM. Grafana on the Ubuntu VM visualizes the time series.

Network IPs:
- Raspberry Pi (sensors): 10.233.251.70
- Ubuntu VM1 (InfluxDB + Grafana + Prometheus): 10.233.251.71

Data model:
- InfluxDB org: microgrid
- InfluxDB bucket: telemetry
- Measurements: bme280, veml7700
- Tag: host = rpi-10.233.251.70
- Fields:
  - bme280: temperature_c, humidity_pct, pressure_hpa
  - veml7700: lux, white

---

# Part A: Ubuntu VM1 (10.233.251.71) Stack

All VM1 configs and persistent data are stored under:
 /home/alpha/Capstone/influxDB

## A1) Install Docker Engine + Docker Compose plugin (Ubuntu)

sudo apt update
sudo apt install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker

docker version
docker compose version

## A2) Create VM1 folder structure

sudo mkdir -p /home/alpha/Capstone/influxDB/prometheus/data
sudo mkdir -p /home/alpha/Capstone/influxDB/telegraf
sudo mkdir -p /home/alpha/Capstone/influxDB/grafana/data
sudo mkdir -p /home/alpha/Capstone/influxDB/grafana/provisioning
sudo mkdir -p /home/alpha/Capstone/influxDB/influxdb/data
sudo mkdir -p /home/alpha/Capstone/influxDB/influxdb/config

## A3) Create Prometheus config

sudo tee /home/alpha/Capstone/influxDB/prometheus/prometheus.yml >/dev/null <<'YAML'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]
YAML

## A4) Create Telegraf config (VM1 metrics to InfluxDB)

sudo tee /home/alpha/Capstone/influxDB/telegraf/telegraf.conf >/dev/null <<'CONF'
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

## A5) Set permissions (VM1)

sudo chown -R 65534:65534 /home/alpha/Capstone/influxDB/prometheus/data
sudo chown -R 472:472 /home/alpha/Capstone/influxDB/grafana/data
sudo chown -R 1000:1000 /home/alpha/Capstone/influxDB/influxdb/data /home/alpha/Capstone/influxDB/influxdb/config || true

## A6) VM1 docker-compose.yml

sudo tee /home/alpha/Capstone/influxDB/docker-compose.yml >/dev/null <<'YAML'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - /home/alpha/Capstone/influxDB/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - /home/alpha/Capstone/influxDB/prometheus/data:/prometheus
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
      - /home/alpha/Capstone/influxDB/influxdb/data:/var/lib/influxdb2
      - /home/alpha/Capstone/influxDB/influxdb/config:/etc/influxdb2
    restart: unless-stopped

  telegraf:
    image: telegraf:latest
    container_name: telegraf
    depends_on:
      - influxdb
    volumes:
      - /home/alpha/Capstone/influxDB/telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
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
      - /home/alpha/Capstone/influxDB/grafana/provisioning:/etc/grafana/provisioning:ro
      - /home/alpha/Capstone/influxDB/grafana/data:/var/lib/grafana
    restart: unless-stopped
YAML

## A7) Start the stack (VM1)

cd /home/alpha/Capstone/influxDB
docker compose up -d
docker compose ps

VM1 access:
- InfluxDB UI: http://10.233.251.71:8086
  - user: admin
  - pw: adminpass
  - org: microgrid
  - bucket: telemetry
  - admin token (set by init): admintoken==
- Grafana UI: http://10.233.251.71:3000
  - user: admin
  - pw: grafana
- Prometheus UI: http://10.233.251.71:9090

VM1 troubleshooting:
cd /home/alpha/Capstone/influxDB
docker compose logs -f
docker compose logs --tail=200 influxdb
docker compose logs --tail=200 grafana
docker compose logs --tail=200 telegraf
docker compose logs --tail=200 prometheus

Firewall (if needed on VM1):
sudo ufw status
sudo ufw allow 8086/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 9090/tcp

---

# Part B: Raspberry Pi (10.233.251.70) Sensor Agent

The Pi reads sensors locally via I2C and pushes measurements to InfluxDB on VM1 at:
 http://10.233.251.71:8086

## B1) Enable I2C on the Pi

sudo raspi-config

Interface Options -> I2C -> Enable

Confirm device exists and sensors respond:
sudo apt update
sudo apt install -y i2c-tools
ls -l /dev/i2c*
sudo i2cdetect -y 1

Expected addresses typically include:
- BME280: 0x76 or 0x77
- VEML7700: 0x10

## B2) Create Pi sensor-agent project

mkdir -p /home/alpha/sensor-agent
cd /home/alpha/sensor-agent

## B3) Pi docker-compose.yml

sudo tee /home/alpha/sensor-agent/docker-compose.yml >/dev/null <<'YAML'
services:
  sensor-agent:
    build: .
    container_name: sensor-agent
    restart: unless-stopped
    privileged: true
    devices:
      - "/dev/i2c-1:/dev/i2c-1"
    environment:
      INFLUX_URL: "http://10.233.251.71:8086"
      INFLUX_TOKEN: "admintoken=="
      INFLUX_ORG: "microgrid"
      INFLUX_BUCKET: "telemetry"
      SENSOR_HOST: "rpi-10.233.251.70"
      INTERVAL_S: "10"
YAML

Token note:
- For production, generate a dedicated write token in the InfluxDB UI (API Tokens) and replace INFLUX_TOKEN.

## B4) Pi Dockerfile

sudo tee /home/alpha/sensor-agent/Dockerfile >/dev/null <<'DOCKERFILE'
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    i2c-tools \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    influxdb-client \
    adafruit-blinka \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-veml7700 \
    smbus2 \
    RPi.GPIO

COPY app.py /app/app.py
CMD ["python", "-u", "/app/app.py"]
DOCKERFILE

## B5) Pi app.py

sudo tee /home/alpha/sensor-agent/app.py >/dev/null <<'PY'
import os
import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import board
import busio
import adafruit_bme280.basic as adafruit_bme280
import adafruit_veml7700


INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG = os.getenv("INFLUX_ORG", "microgrid")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "telemetry")
SENSOR_HOST = os.getenv("SENSOR_HOST", "rpi")
INTERVAL_S = int(os.getenv("INTERVAL_S", "10"))

if not INFLUX_TOKEN:
    raise SystemExit("INFLUX_TOKEN is required")

i2c = busio.I2C(board.SCL, board.SDA)

bme = None
for addr in (0x76, 0x77):
    try:
        bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=addr)
        break
    except Exception:
        bme = None

if bme is None:
    raise SystemExit("BME280 not detected at 0x76 or 0x77")

veml = adafruit_veml7700.VEML7700(i2c)

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    try:
        temp_c = float(bme.temperature)
        hum = float(bme.humidity)
        pres_hpa = float(bme.pressure)

        lux = float(veml.lux)
        white = float(veml.white)

        ts = time.time_ns()

        p1 = (
            Point("bme280")
            .tag("host", SENSOR_HOST)
            .field("temperature_c", temp_c)
            .field("humidity_pct", hum)
            .field("pressure_hpa", pres_hpa)
            .time(ts, WritePrecision.NS)
        )

        p2 = (
            Point("veml7700")
            .tag("host", SENSOR_HOST)
            .field("lux", lux)
            .field("white", white)
            .time(ts, WritePrecision.NS)
        )

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=[p1, p2])
        print(f"sent: temp={temp_c:.2f}C hum={hum:.2f}% pres={pres_hpa:.2f}hPa lux={lux:.2f} white={white:.2f}")

    except Exception as e:
        print(f"read/write error: {e}")

    time.sleep(INTERVAL_S)
PY

## B6) Start sensor-agent on the Pi

cd /home/alpha/sensor-agent
docker compose up -d --build
docker compose logs -f

Pi troubleshooting:
cd /home/alpha/sensor-agent
docker compose ps
docker compose logs --tail=200 sensor-agent
docker exec -it sensor-agent ls -l /dev/i2c-1
date
timedatectl

---

# Part C: Verify Data Is Arriving in InfluxDB

## C1) Verify from the InfluxDB UI

Open:
 http://10.233.251.71:8086

Data Explorer:
- Bucket: telemetry
- _measurement: bme280 and veml7700
- host: rpi-10.233.251.70
- fields: temperature_c, humidity_pct, pressure_hpa, lux, white
Time range must include recent time (Last 15m or Last 1h).

## C2) Verify from VM1 using CLI

docker exec -it influxdb influx query '
from(bucket:"telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r.host == "rpi-10.233.251.70")
  |> filter(fn: (r) => r._measurement == "bme280" or r._measurement == "veml7700")
  |> last()
' --org microgrid --token "admintoken=="

If host tag differs, discover distinct host values:
docker exec -it influxdb influx query '
from(bucket:"telemetry")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "bme280" or r._measurement == "veml7700")
  |> keep(columns: ["host"])
  |> group()
  |> distinct(column: "host")
' --org microgrid --token "admintoken=="

## C3) Verify from the Pi by writing a single test point

TOKEN="admintoken=="
curl -i -X POST "http://10.233.251.71:8086/api/v2/write?org=microgrid&bucket=telemetry&precision=s" \
  -H "Authorization: Token $TOKEN" \
  --data-raw "net_test,host=rpi-10.233.251.70 value=1 $(date +%s)"

Expected: HTTP/1.1 204 No Content

---

# Part D: Grafana Quick Use

Open:
 http://10.233.251.71:3000

Login:
- user: admin
- pw: grafana

Explore -> pick your InfluxDB datasource -> example Flux query:

from(bucket: "telemetry")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "bme280")
  |> filter(fn: (r) => r.host == "rpi-10.233.251.70")
  |> filter(fn: (r) => r._field == "temperature_c")
  |> aggregateWindow(every: 10s, fn: mean, createEmpty: false)
