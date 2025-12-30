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
