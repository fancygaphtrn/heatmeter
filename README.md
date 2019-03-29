# heatmeter
heatmeter custom sensor for home assistant

### Getting started

* Add sensor.py to the Home Assistant <config>\custom_components\heatmeter directory

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
* [voltlet](https://github.com/mcolyer/voltlet) the inspiration. Wrote in python because I wanted to learn the language.
* [vesync-wsproxy](https://github.com/itsnotlupus/vesync-wsproxy) this project just proxies the connect to the cloud server to spy on what happens. I'd rather keep my data local.
* This [project](https://github.com/travissinnott/outlet) attempted to do something similar but wasn't fully implemented. That said it has great notes about the line protocol


[Etekcity Voltson]: https://www.amazon.com/gp/product/B06XSTJST6/ref=as_li_tl?ie=UTF8&camp=1789&creative=9325&creativeASIN=B06XSTJST6&linkCode=as2&tag=matcol01-20&linkId=ab8750e61f7f9723ddaa60cb56d0df82
