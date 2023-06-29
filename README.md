

# GiZMo's Home Assistant add-on repository


[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/GiZMoSK1221/hass-addons)

## Add-ons

This repository contains the following add-ons

### [Netatmo Favorites Weather Stations add-on](./nfws)

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

_Netatmo integration for Home Assistant. You can get data from your favorite weather stations in Netatmo._

### [Wattsonic gen3 modbus configs](./wattsonic)
Forum: https://community.home-assistant.io/t/wattsonic-photovoltaic-power-plant-fve-integration/406135

### [Etrel inch modbus configs](./etrel_inch)
Forum: https://community.home-assistant.io/t/etrel-inch-modbus-tcp-communication/548968

### [Appdaemon Electric Consumption Db Repair tool](./ElectricConsumptionDbRepair)
Script tries to repair statistics, wrong received data from sensor. Typically when one value is too high and scrambles charts in energy dashboard
Forum: N/A


### [ParadoxPRT3toMQTT add-on](./)
tbd, based on [ParadoxHassMQTT](https://github.com/DaveOke/ParadoxHassMQTT) project, integrated into Home Assistant as add-on
Integrates Paradox Digiplex DGP-848 control panel with PRT3 printer module->USB->RPi4 using ASCII PRT3 protocol

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
