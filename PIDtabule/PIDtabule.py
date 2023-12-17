#https://www.homeassistant-cz.cz/viewtopic.php?t=751
#API kluc - https://api.golemio.cz/api-keys/auth/sign-in
#swagger - https://api.golemio.cz/v2/pid/docs/openapi/
#ID zastavky - http://data.pid.cz/stops/xml/StopsByName.xml
import appdaemon.plugins.hass.hassapi as hass
import datetime
import requests

class PIDtabuleClass(hass.Hass):

  def mylog(self, text):
    log = ""
    if "log" in self.args["config"]:
        log = self.args["config"]["log"]
    if log !="":
        try:
            self.log(text, log=f"{log}")
        except BaseException as err:
            self.log(text)
    else:
        self.log(text)


  def main_pid(self, cb_args):
    config = self.args["config"]
    if "gtfsIds" not in config:
      self.mylog(f"Missing gtfsIds in config")
      return
    
    gtfsIds = config["gtfsIds"]
    gtfsIds_url = ""
    for gtfsId in gtfsIds:
      gtfsIds_url = gtfsIds_url + f"ids={gtfsId}&"
    api_url = f'https://api.golemio.cz/v2/pid/departureboards?{gtfsIds_url}&preferredTimezone=Europe%2FPrague&limit={config["connection_limit"]}{config["api_param"]}'
    headers =  {"Content-Type":"application/json; charset=utf-8", "X-Access-Token":f"{config['golemio_token']}"}
    try:
      response = requests.get(api_url, headers=headers)
    except BaseException as err:
      self.mylog(f"Unexpected request result {err=}, {type(err)=}")
      self.mylog(api_url)
      return
    json = response.json()
    #self.mylog(response.headers)
    #self.mylog(json)
    if response.status_code != requests.codes.ok:
      self.mylog(f"Wrong result code: {response}")
      #401=wrong token
      return

    connection_list = []
    for departure in json["departures"]:
      trip_headsign = departure["trip"]["headsign"]  #cielova stanica
      if "only_destination_names" not in config or trip_headsign in config["only_destination_names"]:
        route_short_name = departure["route"]["short_name"] #cislo spoja
        if "only_connection_names" not in config or route_short_name in config["only_connection_names"]:
          trip_short_name = departure["trip"]["short_name"]  #cislo vlaku
          predicted = departure["arrival_timestamp"]["predicted"]
          predicted_time = datetime.datetime.fromisoformat(predicted).time()
          if predicted_time.minute < 10:
            predicted_time_rounded = f"{predicted_time.hour}:0{predicted_time.minute}"
          else:
            predicted_time_rounded = f"{predicted_time.hour}:{predicted_time.minute}"
          predicted_est = round((datetime.datetime.fromisoformat(predicted).timestamp()-datetime.datetime.now().timestamp()) // 60)
          last_stop_name = departure["last_stop"]["name"]  #nazov poslednej zastavky
          if last_stop_name is None:
            last_stop_name = ""
          delay = 0
          if departure["delay"]["is_available"] == True:
            delay = departure["delay"]["minutes"]
          #self.mylog(f'{route_short_name} to {trip_headsign} at {predicted_time_rounded}, in {predicted_est} min, meska: {delay} minut')
          connection_list.append({"arrival_timestamp_predicted_time":f"{predicted_time_rounded}", 
                                  "arrival_timestamp_predicted_est":f"{predicted_est}", 
                                  "route_short_name":f"{route_short_name}",                          #cislo spoja - S22
                                  "trip_short_name":f"{trip_short_name}",                            #cislo vlaku - os8123
                                  "trip_headsign":f"{trip_headsign}",                                #cielova stanica
                                  "delay":f"{delay}",
                                  "last_stop_name":f"{last_stop_name}" 
                                  })
          
    state_attr = {"friendly_name": "PID tabule",
                  "updated": f"{datetime.datetime.now()}",
                  "data": connection_list
                  }
    #, "unique_id": "PIDtabule"}
#    state_state = f'{connection_list[0]["route_short_name"]}/{connection_list[0]["trip_short_name"]} do {connection_list[0]["trip_headsign"]} za {connection_list[0]["predicted_est"]} min'
    state_state = f'{connection_list[0]["route_short_name"]} za {connection_list[0]["arrival_timestamp_predicted_est"]} min'
    #self.mylog(state_state)
    self.set_state("sensor.PIDtabule", state = state_state, attributes = state_attr)

  def initialize(self):
    self.mylog("PIDTabule start --------------------------------------------------------")

    self.main_pid(self)

    runtime = datetime.time(0, 0, 0)
    self.run_minutely(self.main_pid, runtime)
