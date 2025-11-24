# Work items

Prompts:
1. `based on the mermaid diagram, create a very high level markdown checkbox list of work items needed. only go one or two levels deep if really needed`
2. `the DER devices should be developed by us, modify the work list to account for that`

## Phase 1: DER Device Development & Data Pipeline
- [ ] Develop DER devices / simulators
  - [ ] Wind turbine simulator → MQTT
  - [ ] Solar PV simulator → Modbus
  - [ ] Battery storage simulator → HTTP
- [ ] Implement device telemetry protocols
  - [ ] MQTT publish for Wind
  - [ ] Modbus TCP registers for Solar
  - [ ] HTTP POST for Battery
- [ ] Deploy databases
  - [ ] Deploy Prometheus
  - [ ] Deploy InfluxDB
- [ ] Deploy Mosquitto MQTT broker
- [ ] Deploy Telegraf pipelines
  - [ ] MQTT subscriber
  - [ ] Modbus poller
  - [ ] HTTP listener
- [ ] Connect Telegraf outputs to InfluxDB and Prometheus
- [ ] Verify data ingestion from DER devices

## Phase 2: Monitoring & Alerting
- [ ] Deploy Grafana dashboards
  - [ ] Connect to InfluxDB
  - [ ] Connect to Prometheus
- [ ] Deploy Alertmanager
- [ ] Define alert rules
  - [ ] High load
  - [ ] Low SOC
  - [ ] Device offline / communication errors
- [ ] Test alert notifications (email, Slack, etc.)

## Phase 3: Analytics Integration
- [ ] Integrate Analytics Engine with InfluxDB
- [ ] Implement forecasting models
  - [ ] Load demand
  - [ ] Renewable generation
  - [ ] Battery SOC trends
- [ ] Store forecasted metrics back in InfluxDB
- [ ] Update Grafana dashboards with predictions

## Phase 4: Automation Module
- [ ] Connect Automation Module to:
  - [ ] Real-time telemetry
  - [ ] Analytics forecasts
- [ ] Implement DER scheduling and load management
- [ ] Send control signals to DERs (MQTT/HTTP/Modbus)
- [ ] Test automation under normal and edge-case scenarios

## Phase 5: Weather Integration
- [ ] Integrate weather forecast data into InfluxDB
- [ ] Use weather data in Analytics Engine
- [ ] Validate impact on automation decisions

## Phase 6: End-to-End Testing & Validation
- [ ] Simulate operational scenarios
  - [ ] High demand peaks
  - [ ] Low renewable generation
  - [ ] Outages or DER failures
- [ ] Validate telemetry ingestion and storage
- [ ] Validate forecast accuracy
- [ ] Validate automation decisions and DER responses
- [ ] Validate alert triggering and notifications
- [ ] Validate dashboard visualizations
- [ ] Iterate improvements based on tests

## Phase X: rpi weather station (TBD)
