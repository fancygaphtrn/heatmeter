# heatmeter
heatmeter custom sensor for home assistant

### Getting started

* Add sensor.py to the Home Assistant config\custom_components\heatmeter directory

#### Home Assistant Example

```
configuration.yaml

sensor:
  - platform: heatmeter
    host: <Hostname of heatmeter>
    port: 80
    username: PORTAL_LOGIN
    password: PORTAL_PASSWORD
    scan_interval: 2
```

### References
Support for reading Heatmeter data. See https://store.heatermeter.com/
