
# Home Assistant Add-on: Netatmo Favorites Weather Station

## Preconditions

### Home Assistant
 - installed MQTT broker addon
 - enabled MQTT discovery

### Netatmo
- Netatmo [account](https://auth.netatmo.com/access/checklogin)
- Netatmo App created at [developer page](https://dev.netatmo.com/)
![](https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_new_app.jpg)
- client_id and client_secret from your app
![](https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_ids.jpg)
- at least one [favorite station](https://weathermap.netatmo.com/?zoom=15&maplayer=Map)
![](https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_add_fav.jpg)


## Installation and first run

 - install the addon
 [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/GiZMoSK1221/hass-addons)

 - go to config tab and enter your client_id and client_secret. Run addon, wait few seconds, stop addon
 - go to log tab. You will see there this message:
 >Missing Netatmo authorisation OAUTH code!
When access granted, copy code value from returned url to config.yaml
Example of returned URL: https://app.netatmo.net/oauth2/hassio?state=nfws_hass&code=5ebbe91cdd804326ddde4336c7e9b6b8
Calling...https://api.netatmo.com/oauth2/authorize?client_id=60e5c04fef24f51a5d36c03a&redirect_uri=hassio&scope=read_station&state=nfws_hass

- copy&paste URL to a new window and grant access
![](https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_accept.jpg)

- Netatmo will redirect your browser to app.netatmo.net with error 404. Just copy OAUTH code from code section from URL  (code=OAUTH code)
![](https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/main/nfws/help/netatmo_accept_code.jpg)

- goto config tab and enter OAUTH code. 
- run addon
do last 3 steps quickly. Otherwise you might get:
Netatmo authorization_code: Wrong response code 400
{'error': 'expired_token'}

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

- Not used station section shows MAC address of your favourites stations

Now, you were able tu run successfully the addon for the first time. Now, go to hass config/nfws directory and edit stations.yaml using MAC addresses you got.

## Configuring add-on
### stations.yaml
[stations.yaml example](https://github.com/GiZMoSK1221/hass-addons/blob/main/nfws/help/stations_example.yaml) with parameters description

### Addon configuration tab
- netatmo->refresh_interval: how often in minutes should addon retrieve data
-   nfws->deleteRetain: true deletes all sensors on startup created by addon. Use once when your configuration is finished to delete orphaned sensors     
-  netatmo->log_level: possible values are: debug|info|warning|error|critical. Change to warning or info when addon runs correctly
 
## Troubleshooting
### Any problem with token, token not valid, new cannot be obtained
1. stop addon
2. delete netatmo_token.yaml
3. in config tab set oauth_code: ""
4. run addon. stop addon
5. go to log, copy url and open it in a new browser tab/window. Allow plugin to access netatmo data 
6. get code value from url, close tab/window
7. go to log, enter oauth_code: 'code'
8. start addon