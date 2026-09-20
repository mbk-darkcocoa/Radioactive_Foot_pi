# Radioactive_Foot_pi
A repository for Radioactive_Foot_pi application code and supporting automation assets.

## Vagrant LAN/WAN setup

- `Vagrantfile` creates a VM with a private LAN on `192.168.56.10` by default.
- Set `RADIOACTIVE_FOOT_PI_LAN` to `false`, `0`, `no`, or `off` to disable the private LAN adapter.
- Set `RADIOACTIVE_FOOT_PI_LAN_IP` to override the default private LAN address.
- Set `RADIOACTIVE_FOOT_PI_WAN` to `true`, `1`, `yes`, or `on` to add a bridged/public WAN adapter.
- Set `RADIOACTIVE_FOOT_PI_WAN_BRIDGE` to pin the WAN adapter to a specific host bridge.
- Set `RADIOACTIVE_FOOT_PI_OS=ubuntu` or `RADIOACTIVE_FOOT_PI_OS=fedora` to choose the base box.
- Optional sizing overrides: `RADIOACTIVE_FOOT_PI_CPUS`, `RADIOACTIVE_FOOT_PI_MEMORY`, and `RADIOACTIVE_FOOT_PI_HOSTNAME`.

## Apify helper files

- `docs/apify-web-scraper-input.json` contains an example input payload for the Apify `apify/web-scraper` actor.
- `docs/run-apify-web-scraper.sh` posts that payload to the Apify actor run endpoint.
