


# <img src="https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/icon.png" alt="drawing" width="50"/> Home Assistant Add-on: Netatmo Favorites Weather Station  
[![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif)](https://www.paypal.com/donate/?business=XTWWUQFKVX2XJ&no_recurring=1&item_name=Home+Assistent+Addons&currency_code=CZK)

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports i386 Architecture][i386-shield]

Netatmo public weather stations integration for Home Assistant . You can receive data from your favourite weather stations in your Netatmo account,
![][netatmo_favorites_list]
like:
 - Netatmo data: WindAngle, GustAngle, Humidity, Pressure, rain, sum_rain_1, sum_rain_24, WindStrength, GustStrength, Temperature
 - Wind directions(NESW)/Symbols(↓↙→): WindAngleCompass, WindAngleCompassSymbol, GustAngleCompass, GustAngleCompassSymbol
 - Calculated values from station list: first available value, minimal/maximal/average value

This addon enables user without Netatmo hardware to use public weather data and use them in automations, like

 - automate irrigation according to rain, temperature
 - automate blinds according to wind, wind gust and direction
 - many more


![][netatmo_screenshot]

Config example: [stations_example.yaml](https://github.com/GiZMoSK1221/hass-addons/blob/main/nfws/help/stations_example.yaml)

**Background**: 
Netatmo offers a [getpublicdata API](https://dev.netatmo.com/apidocumentation/weather#getpublicdata), which allows you to retrieve publicly shared weather data from Outdoors Modules within a predefined area. There are two main issues I was facing:
1. you don't know what you get - when you have a favourite weather station and you trust it's data, even when you provide exact coordinates, you must not get this station in answer
2. from my observation, wind modules often disappear or don't return data. When you need wind gust to raise venetian blinds to protect them, you need to trust your system and be sure, that you always get this value

**Solution - NFWS addon:** 
1. Netatmo also offers [getstationsdata API](https://dev.netatmo.com/apidocumentation/weather#getstationsdata), which returns user Weather Stations Data. Using parameter get_favorites you get your favourites station from your Netatmo account. Maximum is five stations.
4. Calculated values - function first - retrieves desired value from first available station defined in your list. You just find 5 stations in you surroundings and you have a good chance, that at least one works :)

**Requirements, installation and configuration:**
read [DOCS.md](https://github.com/GiZMoSK1221/hass-addons/blob/main/nfws/DOCS.md)

Forum: https://community.home-assistant.io/t/netatmo-favorites-weather-station-addon/467534

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
[netatmo_favorites_list]: https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_favorites_list.png
[netatmo_screenshot]: https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_screenshot.png

