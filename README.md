# heatmeter smoker controller
heatmeter smoker controller custom sensor for home assistant

### Getting started

* Add sensor.py, __init__.py, services.yaml and manifest.json to the Home Assistant config\custom_components\heatmeter directory

#### Home Assistant Example

```
configuration.yaml

heatmeter:
  host: <Hostname of heatmeter>
  port: 80
  username: PORTAL_LOGIN
  password: PORTAL_PASSWORD

input_number:
  setpoint:
    name: Setpoint
    min: 100
    max: 350
    step: 1   
    mode: box    
    unit_of_measurement: "F"
    icon: mdi:thermometer
```
```
automation.yaml

- id: '10000000000025'
  alias: Update heatmeter setpoint
  trigger:
  - entity_id: input_number.setpoint
    platform: state
  condition: []
  action:
  - service: heatmeter.set_temperature
    data_template:
      temperature: '{{ states.input_number.setpoint.state|int }}'
```
```
ui-lovelace.yaml

  - title: Smoker
    cards:
      - type: entities
        title: Smoker
        show_header_toggle: false
        entities:
          - input_number.setpoint
          - heatmeter.setpoint
          - heatmeter.lid
          - heatmeter.fan
          - heatmeter.probe0_temperature
          - heatmeter.probe1_temperature
          - heatmeter.probe2_temperature
      - type: history-graph
        hours_to_show: 12
        refresh_interval: 10
        entities:
          - heatmeter.setpoint
          - heatmeter.probe0_temperature
          - heatmeter.probe1_temperature
          - heatmeter.probe2_temperature

```

#### Debug
```
To set the log level to debug add debug to the configuration.yaml

logger:
  default: info
    custom_components.heatmeter: debug
```


### References
Support for reading Heatmeter data. See https://store.heatermeter.com/
