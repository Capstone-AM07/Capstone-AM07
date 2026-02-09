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

SOLAR_MEASUREMENT = os.getenv("SOLAR_MEASUREMENT", "solar_estimate")
K_LUX_PER_WM2 = float(os.getenv("K_LUX_PER_WM2", "120"))
PANEL_EFFICIENCY = float(os.getenv("PANEL_EFFICIENCY", "0.20"))
PERFORMANCE_RATIO = float(os.getenv("PERFORMANCE_RATIO", "0.80"))
PANEL_AREA_M2 = float(os.getenv("PANEL_AREA_M2", "0"))

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

        irradiance_wm2 = lux / K_LUX_PER_WM2 if K_LUX_PER_WM2 > 0 else 0.0
        pv_dc_wm2 = irradiance_wm2 * PANEL_EFFICIENCY
        pv_ac_wm2 = pv_dc_wm2 * PERFORMANCE_RATIO
        pv_ac_w = pv_ac_wm2 * PANEL_AREA_M2 if PANEL_AREA_M2 > 0 else 0.0

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

        p3 = (
            Point(SOLAR_MEASUREMENT)
            .tag("host", SENSOR_HOST)
            .field("lux", lux)
            .field("irradiance_wm2", irradiance_wm2)
            .field("pv_dc_wm2", pv_dc_wm2)
            .field("pv_ac_wm2", pv_ac_wm2)
            .field("pv_ac_w", pv_ac_w)
            .time(ts, WritePrecision.NS)
        )

        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=[p1, p2, p3])

        print(
            "sent: "
            f"temp={temp_c:.2f}C hum={hum:.2f}% pres={pres_hpa:.2f}hPa "
            f"lux={lux:.2f} white={white:.2f} "
            f"irr={irradiance_wm2:.1f}W/m2 pv_ac={pv_ac_wm2:.1f}W/m2"
        )

    except Exception as e:
        print(f"read/write error: {e}")

    time.sleep(INTERVAL_S)
