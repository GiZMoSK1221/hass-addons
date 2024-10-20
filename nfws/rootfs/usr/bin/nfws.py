import requests
import json
import paho.mqtt.client as paho
from jsonpath_ng.ext import parse
from datetime import datetime, timezone
import time
import yaml
import webbrowser
import logging
import os
import shutil

#---global constants
# netatmo_module_config= {"Temperature" : ["Temperature"], 
                        # "Humidity" : ["Humidity"], 
                        # "Rain" : ["Rain", "sum_rain_1", "sum_rain_24"], 
                        # "Wind" : ["WindStrength", "WindAngle", "GustStrength", "GustAngle"]
                        # }

#---global variables
registered_entity = {}
netatmo_not_used_stations = []
config_dir = ""
run_mode = ""  #local, hass
global mqtt_client

def get_dict_value(dictv, key, default = "None"):
    if key in dictv:
        return dictv[key]
    else:
        return default

def debug_log(text):
    if get_dict_value(config["nfws"], "log_level") == "debug":
        logger.debug(snow() + text)

def prepare_hass_addon():

    if run_mode != "hass":
        return False

##delete when copy from old location ot needed
    try:
        res_old_config = os.listdir(rf'/homeassistant/nfws/')
    except BaseException as err:
        res_old_config = []
##delete

    try:     
#        logger.critical(f"Directory1: {os.listdir(r'/config/')}")
        res_config = os.listdir(rf'{config_dir}')
        if not "stations.yaml" in res_config:
##delete
            if "stations.yaml" in res_old_config and "netatmo_token.yaml" in res_old_config:    #migration from old config location
                try:
                    logger.debug(f'Old config files found in /homeassistant/nfws/')
                    shutil.copyfile('/homeassistant/nfws/stations.yaml', f'{config_dir}stations.yaml')
                    shutil.copyfile('/homeassistant/nfws/netatmo_token.yaml', f'{config_dir}netatmo_token.yaml')
                except BaseException as err:
                    logger.critical(f'Cannot copy old config files from /config/nfws to {config_dir}')
                    logger.critical(f'Copy netatmo_token.yaml and stations.yaml manually and restart addon')
                    exit()
            else:   #first run stations.yaml doesn't exists
##delete            
                try:
                    logger.debug(f'New installation, copy default stations.yaml, please change it.')
                    shutil.copyfile('/usr/bin/stations.yaml', f'{config_dir}stations.yaml')
                except BaseException as err:
                    logger.critical(f'Cannot copy stations.yaml to {config_dir}')
                    exit()
    except BaseException as err:
        return False

    return True

def load_config():
    global config
    global netatmo_stations
    global params
    global config_dir
    global run_mode

#    logger.debug(f"Run mode: {os.environ}")

    if "SUPERVISOR_TOKEN" in os.environ:
        config_dir = "/config/"
#        config_dir = os.getenv('HOSTNAME')+"/"
        run_mode = "hass"
    else:
        run_mode = "local"

    prepare_hass_addon()

    if run_mode == "hass":
        try:
            with open('/data/options.json', 'r') as file:
                config = json.load(file)
        except BaseException as err:
            logger.critical(f"{snow()}/data/options.json missing {err=}, {type(err)=}")
            exit()
    else:
        try:
            with open(r'options.yaml') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        except BaseException as err:
            logger.critical(f"{snow()}options.yaml missing {err=}, {type(err)=}")
            exit()
    
    #logger.critical(config)
    #exit()

    try:
        with open(config_dir+r'stations.yaml') as file:
            config_stations = yaml.load(file, Loader=yaml.FullLoader)
    except BaseException as err:
        logger.critical(f"{snow()}{config_dir}stations.yaml missing {err=}, {type(err)=}")
        logger.debug(f"Run mode: {run_mode}")
        logger.debug(f"Config dir: {config_dir}")
        exit()
    config.update(config_stations)

    if get_dict_value(config["nfws"], "log_level") != "None":
        logger.setLevel(get_dict_value(config["nfws"], "log_level").upper())

    logger.debug(f"Run mode: {run_mode}")
    logger.debug(f"Config dir: {config_dir}")
    
    if "nfws" not in config:
        config["nfws"] = "None"
    if "netatmo" not in config:
        logger.critical("netatmo section in config missing")
        exit()
    if run_mode != "hass" and "mqtt" not in config:
        logger.critical("mqtt section in config missing")
        exit()
    if "netatmo_stations" not in config:
        logger.critical("netatmo_stations section in stations.yaml missing")
        exit()
    
    if config["netatmo"]["client_id"] == "":
        logger.critical("Netatmo client_id is empty!")
        exit()
    if config["netatmo"]["client_secret"] == "":
        logger.critical("Netatmo client_secret is empty!")
        exit()
    
    if "redirect_uri" not in config["netatmo"]:
        (config["netatmo"])["redirect_uri"] = "hassio"
    if "state" not in config["netatmo"]:
        (config["netatmo"])["state"] = "nfws_hass"

    netatmo_stations = config["netatmo_stations"]
    params = {
        'device_id': '00:00:00:00:00:00',
        'get_favorites': 'true',
    }
    params["device_id"] = next(iter(netatmo_stations))  #get first station from list
    #print(next(iter(netatmo_stations)))

    return True

def load_netatmo_token():
    global netatmo_token

    try:
        with open(config_dir+r'netatmo_token.yaml') as file:
            netatmo_token = yaml.load(file, Loader=yaml.FullLoader)
    except BaseException as err:
        netatmo_token = {}
    
    #print(netatmo_token)
    
    if "refresh_token" not in netatmo_token:
        netatmo_token["refresh_token"] = ""
    if "access_token" not in netatmo_token:
        netatmo_token["access_token"] = ""

    return True


def degToCompass(num):
#https://stackoverflow.com/questions/7490660/converting-wind-direction-in-angles-to-text-words
    val = int((num/45)+.5)
    arr = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return arr[(val % 8)]
def degToCompassSymbol(num):
    val = int((num/45)+.5)
#    arr = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
    arr = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]
    return arr[(val % 8)]

def snow():
    #return datetime.now().strftime("%d.%m.%Y %H:%M:%S")+" "
    utc_dt = datetime.now(timezone.utc)
    return utc_dt.astimezone().strftime("%d.%m.%Y %H:%M:%S") + " "

def netatmo_check_oauth_code():
    client = get_dict_value(config["netatmo"], "oauth_code", "")
    if client == "":
        logger.critical(f"{snow()}Missing Netatmo authorisation OAUTH code!")
        logger.critical(f"When access granted, copy code value from returned url to config.yaml")
        logger.critical(f"Example of returned URL: https://app.netatmo.net/oauth2/hassio?state=nfws_hass&code=5ebbe91cdd814823ddfe4336a7e9b6b8")
        client_id = config["netatmo"]["client_id"]
        uri = config["netatmo"]["redirect_uri"]
        state = config["netatmo"]["state"]
        url = f"https://api.netatmo.com/oauth2/authorize?client_id={client_id}&redirect_uri={uri}&scope=read_station&state={state}"
        logger.critical(f"")
        logger.critical(f"Calling...{url}")
        #webbrowser.open_new(url)
        logger.critical(f"Copy&paste the url to a new window and get your OAUTH code")
        logger.critical(f"Delete netatmo_token.yaml if it exists in config directory.")
        logger.critical(f"when done, restart addon...")
        time.sleep(600)
        exit()
        
    return 1

def netatmo_get_oauth_token():
    global netatmo_token
    client_id = config["netatmo"]["client_id"]
    client_secret = config["netatmo"]["client_secret"]
    uri = config["netatmo"]["redirect_uri"]
    code = config["netatmo"]["oauth_code"]
    refresh_token = netatmo_token["refresh_token"]
    
    if refresh_token != "":
        data = f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}"
        method = "Netatmo refresh_token"
    else:
        data = f"grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&code={code}&redirect_uri={uri}&scope=read_station"
        method = "Netatmo authorization_code"

    #logger.debug(data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded',}
    response_ok = False

    while not response_ok:
        try:
            response = requests.post('https://api.netatmo.com/oauth2/token', headers=headers, data=data)
        except BaseException as err:
            logger.error(f"{snow()}Unexpected {method} {err=}, {type(err)=}")
            logger.error("  Retry in 1 min again")
            time.sleep(60) 
            continue

        if response.status_code != requests.codes.ok:
            logger.warning(f"{method}: Wrong response code {response.status_code}")
            json_token=response.json()
            logger.warning(json_token)
            logger.warning("  Retry in 1 min again")
            time.sleep(60)
            continue
    
        json_token = response.json()
        logger.debug(json.dumps(json_token, indent = 4, sort_keys=True))
        if "access_token" not in json_token:
            logger.warning(snow() + f"{method}: Acces token is missing in response")
            logger.warning("  Retry in 1 min again")
            time.sleep(60)
            continue
        response_ok = True
        netatmo_token = response.json()
        
        #access_token = json_token["access_token"]
        #refresh_token = json_token["refresh_token"]

        try:
            with open(config_dir+r'netatmo_token.yaml', 'w') as file:
                documents = yaml.dump(json_token, file)
        except BaseException as err:
            logger.critical(f"{snow()}Cannot write netatmo_token.yaml {err=}, {type(err)=}")
            time.sleep(60)
            exit()

    return 1

def netatmo_refresh_token():
    global netatmo_token    
    client_id = config["netatmo"]["client_id"]
    client_secret = config["netatmo"]["client_secret"]
    refresh_token = netatmo_token["refresh_token"]
    
    data = f"grant_type=refresh_token&client_id={client_id}&client_secret={client_secret}&refresh_token={refresh_token}"
    print(data)
    headers = {'Content-Type': 'application/x-www-form-urlencoded',}
    response_ok = False

    while not response_ok:
        try:
            response = requests.post('https://api.netatmo.com/oauth2/token', headers=headers, data=data)
        except BaseException as err:
            print(f"{snow()}Unexpected netatmo_refresh_token {err=}, {type(err)=}")
            json_token=response.json()
            print(json_token)
            print("  Retry in 1 min again")
            time.sleep(60)
            continue

        if response.status_code != requests.codes.ok:
            print(f"Netatmo_refresh_token: Wrong response code {response.status_code}")
            json_token=response.json()
            print(json_token)
            print("  Retry in 1 min again")
            time.sleep(60)
            continue
    
        json_token=response.json()
        print(json_token)
        print(json.dumps(json_token, indent = 4, sort_keys=True))
        if "access_token" not in json_token:
            print(snow() + "Netatmo_getdata: Acces token is missing in response")
            print("  Retry in 1 min again")
            time.sleep(60)
            continue
        response_ok = True
            
        #access_token = json_token["access_token"]
        netatmo_token = response.json()
        
        try:
            with open(config_dir+r'netatmo_token.yaml', 'w') as file:
                documents = yaml.dump(json_token, file)
        except BaseException as err:
            print(f"{snow()}Cannot write netatmo_token.yaml {err=}, {type(err)=}")
            exit()
        
    return 1


def mqtt_on_connect(client, userdata, flags, rc):
 
    if rc == 0: 
        debug_log("Connected to mqtt broker - mqtt_on_connect")
        registered_entity = {}
    else:
        debug_log("Connection to mqtt broker failed - mqtt_on_connect")
        logger.warning("  Retry in 10 sec again")
        time.sleep(10)
        #mqtt_client.disconnect()
        #mqtt_connect()

def mqtt_disconnect():
    if run_mode != "hass":
        mqtt_client.disconnect()
    return True
        
def mqtt_connect():
    if run_mode == "hass":
        return True

    global mqtt_client
    response_ok = False
    while not response_ok:
        try:
            client = get_dict_value(config["mqtt"], "client", "nwsclient")
            mqtt_client = paho.Client(client)
            if get_dict_value(config["mqtt"], "username", "") != "":
                mqtt_client.username_pw_set(config["mqtt"]["username"], config["mqtt"]["password"])
            mqtt_client.on_connect = mqtt_on_connect
            res = mqtt_client.connect(config["mqtt"]["address"], config["mqtt"]["port"])
            mqtt_client.loop_start()
            if res != 0:
                logger.error(snow()+ "Cannot connect to mqtt broker: " + str(res))
                logger.error("  Retry in 1 min again")
                time.sleep(60)            
            else:
                debug_log("Connected to mqtt broker")
                response_ok = True
                registered_entity = {}
        except BaseException as err:
            logger.error(f"{snow()}Unexpected mqtt_connect {err=}, {type(err)=}")
            logger.error("  Retry in 1 min again")
            time.sleep(60)
    
    return True

def hass_mqtt_publish(topic, value, qos, retain):

    headers = {'Authorization': f"Bearer {os.getenv('SUPERVISOR_TOKEN')}",'content-type': 'application/json' }
    data = {'payload': f"{value}", 'topic': f"{topic}", 'retain': f"{retain}"}
    #logger.debug(data)

    response_ok = False
    while not response_ok:
        if run_mode == "hass":
            try:
                res = requests.request('POST', 'http://supervisor/core/api/services/mqtt/publish', headers=headers, json=data)
                if res.status_code != 200:
                    logger.error(f"{snow()}Error hass_mqtt_publish, not nonnected? =>reconnect? code: {res.rc}  status_code: {res.status_code}")
                    logger.error(f"  {topic}={value}")
                    time.sleep(60)
                else:
                    response_ok = True
            except BaseException as err:
                logger.error(f"{snow()}Unexpected mqtt_publish {err=}, {type(err)=}")
                logger.error("  Retry in 1 min again")
                time.sleep(60)
            
        else:
            try:
                res = mqtt_client.publish(topic, value, qos, retain)
                if res.rc != 0:
                    logger.error(f"{snow()}Error hass_mqtt_publish, not nonnected? =>reconnect? code: {res.rc}")
                    logger.error(f"  {topic}={value}")
                    mqtt_connect()
                else:
                    response_ok = True
                    #print(f"  {topic}={value}")
            except BaseException as err:
                logger.error(f"{snow()}Unexpected mqtt_publish {err=}, {type(err)=}")
                logger.error("  Retry in 1 min again")
                time.sleep(60)
            
    return res

def hass_register_sensor(entity_name, sensor):
#nfws_name_temperature, sensor name
    global registered_entity
    
    if entity_name in registered_entity:
        return False
    
    registered_entity[entity_name] = True 
    hass_conf = {}
    hass_conf["unique_id"] = entity_name
    hass_conf["name"] = entity_name
    hass_conf["state_topic"] = "nfws/sensor/" + entity_name + "/state"
    hass_conf["json_attributes_topic"] = "nfws/sensor/" + entity_name + "/state" #new
    hass_conf["value_template"] = "{{ value_json.value }}" #new
    hass_conf["device"] = {
					"identifiers": ["Netatmo weather station_70ee50"], 
					"name": "Netatmo Favourite Weather Stations", 
					"manufacturer": "Netatmo", 
					"model": "Weather Stations" 
				}
                
    if sensor.lower() != "windanglecompass" and sensor.lower() != "windanglecompasssymbol" and sensor.lower() != "gustanglecompass" and sensor.lower() != "gustanglecompasssymbol":
        hass_conf["state_class"] = "measurement"
    if sensor.lower() == "temperature" or sensor.lower() == "min_temp" or sensor.lower() == "max_temp":
        hass_conf["device_class"] = "temperature"
        hass_conf["unit_of_measurement"] = "°C"
    if sensor.lower() == "humidity":
        hass_conf["device_class"] = "humidity"
        hass_conf["unit_of_measurement"] = "%"
    if sensor.lower() == "pressure":
        hass_conf["device_class"] = "pressure"
        hass_conf["unit_of_measurement"] = "hPa"
    if sensor.lower() == "guststrength" or sensor.lower() == "windstrength":
        hass_conf["unit_of_measurement"] = "km/h"
    if sensor.lower() == "sum_rain_24" or sensor.lower() == "sum_rain_1" or sensor.lower() == "rain":
        hass_conf["unit_of_measurement"] = "mm"
#    if sensor.lower() == "windanglecompass" or sensor.lower() == "windanglecompasssymbol" or sensor.lower() == "gustanglecompass" or sensor.lower() == "gustanglecompasssymbol":
#        hass_conf["state_class"] = ""
    
    logger.info( snow() + "Registering: " + str(hass_conf))
    ret = hass_mqtt_publish("homeassistant/sensor/nfws/" + entity_name + "/config", json.dumps(hass_conf), qos=0, retain=True) 
    #print(ret.rc)

    return True

def hass_publish_station_sensor(station, sensor, value):
#station from config, sensor name, value
    
    if sensor in station["sensors"]:        #is sensor configured?
        hass_register_sensor("nfws_" + station["name"] + "_" + sensor, sensor)

        hass_data = {}
        hass_data["value"] = value
        hass_data["updated_when"] = snow()
        ret = hass_mqtt_publish(f"nfws/sensor/nfws_{station['name']}_{sensor}/state", json.dumps(hass_data, ensure_ascii=False), qos = 0, retain = False) 
        #print(ret.rc)

    return True

def hass_publish_calculated_station_sensor(entity_name, sensor, value):
#calculated station name, sensor name, value
    
    hass_register_sensor(entity_name, sensor)
    
    value["updated_when"] = snow()
    ret = hass_mqtt_publish(f"nfws/sensor/{entity_name}/state", json.dumps(value, ensure_ascii=False), qos = 0, retain = False) 
    #print(ret.rc)

    return True

def netatmo_getdata():
    response_ok = False;
    while not response_ok:
        access_token = netatmo_token["access_token"]
        headers = {'Authorization': f"Bearer {access_token}", }
        try:
            response = requests.get('https://api.netatmo.com/api/getstationsdata', params=params, headers=headers)
        except BaseException as err:
            logger.warning(f"{snow()}Unexpected netatmo_getdata {err=}, {type(err)=}")
            logger.warning("  Retry in 1 min again")
            time.sleep(60)
            continue
        json_netatmo = response.json()
        #print(json_netatmo)
        if get_dict_value(config["netatmo"], "show_response", False) == True:
            #print(json.dumps(json_netatmo, indent = 4, sort_keys=True))
            logger.debug(json_netatmo)
            time.sleep(60)
            
        if "error" in json_netatmo:
            if json_netatmo["error"]["message"] in {"Invalid access token", "Access token expired"}:
                logger.warning(snow() + "Invalid access token or expired:" + json_netatmo["error"]["message"])
                time.sleep(60)
                netatmo_get_oauth_token()
            else:
                logger.error(snow() + json_netatmo["error"]["message"])
                logger.error("  Retry in 1 min again")
                time.sleep(60)
        else:
            response_ok = True
    return json_netatmo

def netatmo_handle_favourite_stations_sensors():
    for device in json_netatmo_devices:
        if device["_id"] not in netatmo_stations:
            if device["_id"] not in netatmo_not_used_stations:
                logger.info(f"Not used station id: {device['_id']}, name: {device['station_name']}")
                netatmo_not_used_stations.append(device["_id"])
            continue
        if device["reachable"] == False:
            continue

        #print(device["station_name"])
        #print(netatmo_stations[device["_id"]])

        hass_publish_station_sensor(netatmo_stations[device["_id"]], "Pressure", device["dashboard_data"]["Pressure"])
        #print(device["dashboard_data"]["Pressure"])
        for module in device["modules"]:
            #print(module["data_type"])
            if module["reachable"] == False:
                continue
            if "data_type" not in module:
                continue
            if "dashboard_data" not in module:
                continue

            if module["data_type"].count("Temperature")!=0:
                if "Temperature" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "Temperature", module["dashboard_data"]["Temperature"])
                if "min_temp" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "min_temp", module["dashboard_data"]["min_temp"])
                if "max_temp" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "max_temp", module["dashboard_data"]["max_temp"])
            if module["data_type"].count("Humidity")!=0:
                if "Humidity" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "Humidity", module["dashboard_data"]["Humidity"])
                    #print(module["dashboard_data"]["Humidity"])
            if module["data_type"].count("Rain")!=0:
                if "Rain" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "rain", module["dashboard_data"]["Rain"])
                    #print(module["dashboard_data"]["Rain"])
                if "sum_rain_1" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "sum_rain_1", module["dashboard_data"]["sum_rain_1"])
                    #print(module["dashboard_data"]["sum_rain_1"])
                if "sum_rain_24" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "sum_rain_24", module["dashboard_data"]["sum_rain_24"])
                    #print(module["dashboard_data"]["sum_rain_24"])
            if module["data_type"].count("Wind")!=0:
                if "WindStrength" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "WindStrength", module["dashboard_data"]["WindStrength"])
                    #print(module["dashboard_data"]["WindStrength"])
                if "WindAngle" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "WindAngle", module["dashboard_data"]["WindAngle"])
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "WindAngleCompass", degToCompass(module["dashboard_data"]["WindAngle"]))  ##odkial fuka
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "WindAngleCompassSymbol", degToCompassSymbol(module["dashboard_data"]["WindAngle"]))  ##odkial fuka
                    #print(module["dashboard_data"]["WindAngle"])
                if "GustStrength" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "GustStrength", module["dashboard_data"]["GustStrength"])
                    #print(module["dashboard_data"]["GustStrength"])
                if "GustAngle" in module["dashboard_data"]:
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "GustAngle", module["dashboard_data"]["GustAngle"])
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "GustAngleCompass", degToCompass(module["dashboard_data"]["GustAngle"]))
                    hass_publish_station_sensor(netatmo_stations[device["_id"]], "GustAngleCompassSymbol", degToCompassSymbol(module["dashboard_data"]["GustAngle"]))
                    #print(module["dashboard_data"]["GustAngle"])

def netatmo_handle_calculated_sensors_function_minmaxavg(function_sensor):
    def Average(lst):
        return round(sum(lst) / len(lst), 1)
        
    #print(function_sensor)
    if "sensors" not in function_sensor:
        return
    if "stations" not in function_sensor:
        return
    for sensor in function_sensor["sensors"]:
        #print(sensor)
        values = []

        for station_id in function_sensor["stations"]:
            #print(station_id)

            if sensor == "Pressure":
                station = parse(f"$.devices[?(@._id == '{station_id}')].dashboard_data.Pressure")
            else:
                station = parse(f"$.devices[?(@._id == '{station_id}')].modules[*].dashboard_data.{sensor}")

            for match in station.find(json_netatmo_body):
                if get_dict_value(match.context.context.value, "reachable", "False") != True:
                    break

                dashboard_data = match.context.value
                #print(dashboard_data[sensor])
                values.append(dashboard_data[sensor])
        value = ""
        if values != []:
            if function_sensor["function"] == "min":
                value = min(values)
            elif function_sensor["function"] == "max":
                value = max(values)
            elif function_sensor["function"] == "avg":
                value = Average(values)
        
        #print(value)
        suffix = ""
        if get_dict_value(function_sensor, "suffix", "") != "":
            suffix = f"_function_sensor['suffix']"
        hass_sensor = f"nfws_{function_sensor['function']}_{sensor}{suffix}"
        hass_sensor_value = {}
        hass_sensor_value["value"] = value
        hass_publish_calculated_station_sensor(hass_sensor, sensor, hass_sensor_value)
        #print(f"{hass_sensor}: {value}")
        

def netatmo_handle_calculated_sensors_function_first(function_sensor):
    if "sensors" not in function_sensor:
        return
    if "stations" not in function_sensor:
        return
    #print(function_sensor)
    first_sensor = next(iter(function_sensor["sensors"]))
    #print(first_sensor)

    found = False
    for station_id in function_sensor["stations"]:
        #print(station_id)
        station = parse(f"$.devices[?(@._id == '{station_id}')].modules[*].dashboard_data.{first_sensor}")

        for match in station.find(json_netatmo_body):
            station_name = f"{match.context.context.context.context.value['station_name']} in {match.context.context.context.context.value['place']['city']}"
            if get_dict_value(match.context.context.value, "reachable", "False") != True:
                debug_log(f"{station_name}: is not reachable")
                break
            if int(get_dict_value(match.context.value, "WindAngle", "500")) < 0:
                debug_log(f"{station_name}: WindAngle is negative")
                break
            timestampdelta = datetime.timestamp(datetime.now(timezone.utc))-int(get_dict_value(match.context.value, 'time_utc', '500'))
            if timestampdelta>=60*int(get_dict_value(function_sensor, "timeDelta", "30")):
                debug_log(f"{station_name}: last update too long")
                break
            
            found = True
            dashboard_data = match.context.value
            #print(dashboard_data)
            
            if first_sensor.lower()[:4] in {"wind", "gust"}:
                dashboard_data["WindAngleCompass"] = degToCompass(dashboard_data["WindAngle"])
                dashboard_data["WindAngleCompassSymbol"] = degToCompassSymbol(dashboard_data["WindAngle"])
                dashboard_data["GustAngleCompass"] = degToCompass(dashboard_data["GustAngle"])
                dashboard_data["GustAngleCompassSymbol"] = degToCompassSymbol(dashboard_data["GustAngle"])
            
            suffix = ""
            if get_dict_value(function_sensor, "suffix", "") != "":
                suffix = f"_function_sensor['suffix']"
            hass_sensor = f"nfws_{function_sensor['function']}_station_name{suffix}"
            #station_name = f"{match.context.context.context.context.value['station_name']} in {match.context.context.context.context.value['place']['city']}"
            
            for sensor in function_sensor["sensors"]:
                hass_sensor = f"nfws_{function_sensor['function']}_{sensor}{suffix}"
                if sensor in dashboard_data:
                    hass_sensor_value = {}
                    hass_sensor_value["value"] = f"{dashboard_data[sensor]}"
                    hass_sensor_value["station_name"] = station_name
                    hass_publish_calculated_station_sensor(hass_sensor, sensor, hass_sensor_value)
                    #print(f"{hass_sensor}: {hass_sensor_value}")
            break
        if found == True:
            break
        debug_log(f"{station_id}: not found in response")

def netatmo_handle_calculated_sensors():
    if "calculated_sensors" not in config:
        return
        
    for function_sensor in config["calculated_sensors"]:
        if function_sensor["function"] == "first":
            netatmo_handle_calculated_sensors_function_first(function_sensor)
        if function_sensor["function"] in {"min", "max", "avg"}:
            netatmo_handle_calculated_sensors_function_minmaxavg(function_sensor)

def hass_mqtt_delete_retain_messages():
    def on_message(client, userdata, msg):
        if msg.retain == 1:
            if get_dict_value(config["nfws"], "log_level") == "debug":
                logger.info(f"Deleting retain topic {msg.topic}")
            hass_mqtt_publish(msg.topic, "", 0, True)
#            hass_mqtt_publish("homeassistant/sensor/nfws/test", "", 0, True)
    global mqtt_client

    if run_mode == "hass":
        return
    if get_dict_value(config["nfws"], "deleteRetain", False) != True:
        return
    logger.info(snow() + "Deleting retain config messages")
    mqtt_client.subscribe("homeassistant/sensor/nfws/#")
    mqtt_client.on_message = on_message
    time.sleep(5)
    mqtt_client.unsubscribe("homeassistant/sensor/nfws/#")


logging.basicConfig(format='%(message)s')  #DEBUG, INFO, WARNING, ERROR, CRITICAL
logger = logging.getLogger('nfws')
logger.setLevel('DEBUG')
logger.info("-------------------------------------------------------------------------------------------------------------")
logger.info(snow() + "Starting Netatmo service")

load_config()
load_netatmo_token()
netatmo_check_oauth_code()

mqtt_connect()
netatmo_get_oauth_token()
hass_mqtt_delete_retain_messages()
mqtt_disconnect()

while True:
    logger.debug(snow() + "get data")

    mqtt_connect()

    json_netatmo = netatmo_getdata()
    json_netatmo_body = json_netatmo["body"]
    #print(json_netatmo_body)
    json_netatmo_devices = json_netatmo_body["devices"]
    #print(json_netatmo_devices)

    netatmo_handle_favourite_stations_sensors()
    netatmo_handle_calculated_sensors()

    mqtt_disconnect()        
    time.sleep(60*get_dict_value(config["netatmo"], "refresh_interval", 1))
