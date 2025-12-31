# Grafana ↔ InfluxDB (Flux) Connection Setup (Telemetry Bucket)

This is a clean summary of the working setup used to connect Grafana to InfluxDB and query the telemetry bucket.

## 1) Create a read token in InfluxDB
1. Open the InfluxDB UI.
2. Go to: Load Data → API Tokens → Generate API Token.
3. Choose a Read Token with access to:
   - Your Org
   - Bucket: telemetry
   - Permission: Read only
4. Copy the token.

## 2) Find your InfluxDB Organization name
In InfluxDB UI:
- Check the org selector in the top header, or
- Go to: Settings → Organizations

Example org used: microgrid

## 3) Add InfluxDB as a Grafana data source (Flux)
1. Grafana → Connections → Data sources → Add data source → InfluxDB
2. Set Query language: Flux
3. Fill in:
   - URL: http://127.0.0.1:8086
     - Using 127.0.0.1 (IPv4) avoids the IPv6 localhost issue ([::1]) that can cause connection refused.
   - Organization: microgrid
   - Token: paste your InfluxDB token
   - Default bucket: telemetry
4. Click Save & test

## 4) Verify Grafana can read from the bucket
Create a panel and run this Flux query:

    from(bucket: "telemetry")
      |> range(start: -15m)
      |> limit(n: 20)

If you see rows in the table output, Grafana is reading data successfully.

## 5) Panel queries for the last 1 hour (by measurement + field)
Set your dashboard time picker to Last 1 hour (top right). These queries follow the dashboard time range.

BME280: temperature_c

    from(bucket: "telemetry")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r._measurement == "bme280")
      |> filter(fn: (r) => r._field == "temperature_c")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

BME280: humidity_pct

    from(bucket: "telemetry")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r._measurement == "bme280")
      |> filter(fn: (r) => r._field == "humidity_pct")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

BME280: pressure_hpa

    from(bucket: "telemetry")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r._measurement == "bme280")
      |> filter(fn: (r) => r._field == "pressure_hpa")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

VEML7700: lux

    from(bucket: "telemetry")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r._measurement == "veml7700")
      |> filter(fn: (r) => r._field == "lux")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

VEML7700: white

    from(bucket: "telemetry")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r._measurement == "veml7700")
      |> filter(fn: (r) => r._field == "white")
      |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)

Optional: hard lock to last 1 hour in the query (ignores dashboard time picker)
Replace the range line with:

    |> range(start: -1h)

## 6) Add °C to a Gauge value
Edit the Gauge panel → Field (Standard options):
- Unit: Temperature → Celsius (°C)

If Unit is not available, set:
- Suffix: °C
