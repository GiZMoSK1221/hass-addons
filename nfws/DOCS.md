# Home Assistant Add-on: Netatmo Favorites Weather Station

## Preconditions

### Home Assistant
 - installed MQTT broker addon
 - enabled MQTT discovery

### Netatmo
- Netatmo [account](https://auth.netatmo.com/access/checklogin)
- at least one favorite station
- MAC addresses of your favorite station. (one is enough for the beginning)
- client_id and client_secret from your app created at [developer page](https://dev.netatmo.com/).
short notice is also on [Netatmo integration page](https://www.home-assistant.io/integrations/netatmo/)

#### How to get MAC address
 - go to [weathermap](https://weathermap.netatmo.com) and login
 - select favorites and first station
 - on station page click share
 - click Copy the link, paste it to notepad:
https://weathermap.netatmo.com//?zoom=15&type=temp&param=NoFilter&stationid=**10%3Aee%3A50%3A28%3A42%3Ac1**&maplayer=Map&lang=sk
 - replace all %3A with :
 - MAC address is:  10:ee:50:28:42:C1

## Installation and first run

 - install the addon
 - go to config tab and enter your client_id and client_secret. Run addon
 - go to log tab. You will see there this message:
 >Missing Netatmo authorisation OAUTH code!
When access granted, copy code value from returned url to config.yaml
Example of returned URL: https://app.netatmo.net/oauth2/hassio?state=nfws_hass&code=5ebbe91cdd804326ddde4336c7e9b6b8
Calling...https://api.netatmo.com/oauth2/authorize?client_id=60e5c04fef24f51a5d36c03a&redirect_uri=hassio&scope=read_station&state=nfws_hass
- copy&paste URL to a new window and grant access
- Netatmo will redirect your browser to app.netatmo.net with error 404. Just copy OAUTH code from code section from URL 
- goto config tab and enter OAUTH code. 
- goto hass config/nfws directory and edit stations.yaml. Change "aa:aa:aa:aa:aa:aa" MAC address to MAC address of you station from preconditions. Save. 
- run addon
- go to log tab. You should see
>11.11.2022 11:11:16 Starting Netatmo service
Run mode: hass
Config dir: /config/nfws/
{
    "access_token": 
}
11.11.2022 11:11:16 get data
11.11.2022 11:11:17 Registering: ....
Not used station id: 70:ee:50:2a:70:14, name: 
Not used station id: 70:ee:50:3c:25:2e, name: 
Not used station id: 70:ee:50:24:18:3a, name: 

- Not used station section shows MAC address of your next favourites stations

Now, you were able tu run successfully the addon for the first time. Now, go to hass config/nfws directory and edit stations.yaml

## Configuring add-on
### stations.yaml
[stations.yaml example](https://github.com/GiZMoSK1221/hass-addons/blob/main/nfws/help/stations_example.yaml) with parameters description

### Addon configuration tab
- netatmo->refresh_interval: how often in minutes should addon retrieve data
-   nfws->deleteRetain: true deletes all sensors on startup created by addon. Use once when your configuration is finished to delete orphaned sensors     
-  netatmo->log_level: possible values are: debug|info|warning|error|critical. Change to warning or info when addon runs correctly
 
