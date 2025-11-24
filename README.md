# Microgrid Data Analytics, Monitoring, and Automation for Remote Communities

### Data flow
1. DERs generate and send telemetry via some communication protocol
    - Some common protocols: Modbus, DNP3, IEC61850, MQTT, HTTP
2. Telegraf ingests and processes all telemetry data and:
    - Pushes data to InfluxDB
    - Exposes data for Prometheus to scrape from
3. Prometheus scrapes metrics and, if needed, triggers alerts via Alertmanager
    - Can send alerts via Email, SMS, Discord, Slack, and more
4. Analytics engine retrieves historical data + weather and forecasts future load and generation
    - Forecasted metrics are pushed back into InfluxDB
6. Automation module retrieves real-time and forecasted metrics and sends control signals to DERs
    - Main control is whether to charge or discharge the battery
7. Grafana dashboards provide visualization of telemetry, forecasts, automation actions, and alerts

### System architecture diagram
```mermaid
flowchart TD

subgraph DERs
    MQTT["Wind<br>(MQTT)"]
    Modbus["Solar<br>(Modbus)"]
    HTTP["Battery<br>(HTTP)"]
end
Mosquitto["Mosquitto<br>(MQTT Broker)"]
subgraph Telegraf
    Telegraf_MQTT["Telegraf<br>(MQTT Subscriber)"]
    Telegraf_Modbus["Telegraf<br>(Modbus Poller)"]
    Telegraf_HTTP["Telegraf<br>(HTTP Server)"]
end
subgraph Time-series Databases
    InfluxDB["InfluxDB<br>(Long-term storage)"]
    Prometheus["Prometheus<br>(Alerting)"]
end
Grafana["Grafana<br>(Visualization)"]
Alertmanager["Alertmanager<br>(Alerting)"]
Analytics["Analytics Engine"]
Automation["Automation Module"]
Weather["Weather Forecast"]

Weather-->|Weather data|InfluxDB
InfluxDB-->|Historical metrics<br>+ Weather data|Analytics
Analytics-->|Forecasted load/gen|InfluxDB
InfluxDB-->|Forecasted load/gen|Automation
Telegraf--->|Real-time metrics|Automation
Automation-->|"DER control signals<br>(Battery charge/discharge)"|DERs

MQTT-->|MQTT publish|Mosquitto
Mosquitto-->|MQTT subscribe|Telegraf_MQTT
Modbus-->|Modbus TCP|Telegraf_Modbus
HTTP-->|HTTP POST|Telegraf_HTTP

Prometheus-->Grafana
InfluxDB-->Grafana

Telegraf--->|Push metrics to InfluxDB|InfluxDB
Telegraf--->|Scrape metrics via endpoint|Prometheus
Prometheus-->Alertmanager
```
