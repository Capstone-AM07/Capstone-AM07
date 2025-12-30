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
