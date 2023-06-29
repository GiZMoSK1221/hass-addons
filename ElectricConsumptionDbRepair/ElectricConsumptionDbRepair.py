import appdaemon.plugins.hass.hassapi as hass
import datetime
import pymysql.cursors
import sqlite3

class RunElectricConsumptionDbRepair(hass.Hass):

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

  def check_entity(self, entity, connection):
    config = self.args["config"]
    cursor = connection.cursor()
    sql = f"""SELECT sst.id as id, sst.metadata_id, sst.state, sst.sum, sm.statistic_id, sst.created_ts FROM statistics sst 
             inner join statistics_meta sm on sm.id=sst.metadata_id and sm.statistic_id='{entity}' 
             order by sst.id desc LIMIT 1"""
    cursor.execute(sql)
    result_last = cursor.fetchone()
    sql = f"""select id, metadata_id, state, sum, statistic_id, created_ts from 
            (SELECT sst.id as id, sst.metadata_id, sst.state, sst.sum, sm.statistic_id, sst.created_ts FROM statistics sst 
             inner join statistics_meta sm on sm.id=sst.metadata_id and sm.statistic_id='{entity}'
             order by id desc LIMIT 2) two 
            order by id ASC limit 1"""
    cursor.execute(sql)
    result_prev = cursor.fetchone()
#    self.mylog(result_last)
    if 'sqlitedb' in config:
      result_last = {
        "id": result_last[0],
        "metadata_id": result_last[1],
        "state": result_last[2],
        "sum": result_last[3],
        "statistic_id": result_last[4],
        "created_ts": result_last[5]
      }
      result_prev = {
        "id": result_prev[0],
        "metadata_id": result_prev[1],
        "state": result_prev[2],
        "sum": result_prev[3],
        "statistic_id": result_prev[4],
        "created_ts": result_prev[5]
      }

    dt_object = datetime.datetime.fromtimestamp(result_last['created_ts'])
    sum_diff = result_last['sum']-result_prev['sum']
    state_diff = result_last['state']-result_prev['state']
    if sum_diff > state_diff+1:
        self.mylog(f"{dt_object} {entity} not ok")
        self.mylog(result_prev)
        self.mylog(result_last)
        #determine what has changed
        if result_last['state']>result_prev['state']:
            #example UPDATE statistics SET sum = sum - (168296.98-89.52) WHERE metadata_id = 36 AND sum > 100
            update_s =              f"""UPDATE statistics SET sum = sum - ({result_last['sum']}-{result_prev['sum']}) WHERE metadata_id = {result_last['metadata_id']} AND sum > {result_prev['sum']} AND created_ts >= {result_prev['created_ts']};"""
            update_sst = f"""UPDATE statistics_short_term SET sum = sum - ({result_last['sum']}-{result_prev['sum']}) WHERE metadata_id = {result_last['metadata_id']} AND sum > {result_prev['sum']} AND created_ts >= {result_prev['created_ts']};"""
            try: 
              self.mylog(update_s)
              self.mylog(update_sst)
              if config["only_logging"] == 0:
                affected_rows = cursor.execute(update_s)
                self.mylog(f"affected_rows = {affected_rows}")
                self.mylog(f"Number of rows is: {cursor.rowcount}")
                affected_rows = cursor.execute(update_sst)
                self.mylog(f"affected_rows = {affected_rows}")
                self.mylog(f"Number of rows is: {cursor.rowcount}")
                connection.commit()
            except MySQLError as e:
                self.mylog(f"{e} -- {e.args[0]}")
        else:
#prev {'id': 2098348, 'metadata_id': 36, 'state': 21496.87, 'sum': 21152.390011330393, 'statistic_id': 'sensor.zw_powerplug_pracka_kwh', 'created_ts': 1685905210.6969206}
#last {'id': 2098566, 'metadata_id': 36, 'state': 607.27,   'sum': 21759.660011330394, 'statistic_id': 'sensor.zw_powerplug_pracka_kwh', 'created_ts': 1685908810.6090727}
#example update statistics_short_term set state=12686.9 where state=1.27 and metadata_id=35 and created_ts >=1686300010.36205
            self.mylog(f"State has changed...update manually")
            update_s =              f"""UPDATE statistics SET state = {result_prev['state']} WHERE metadata_id = {result_last['metadata_id']} AND state = {result_last['state']} AND created_ts >= {result_prev['created_ts']};"""
            self.mylog(update_s)


  def initialize(self):
    self.mylog("Electric consumption db repair start------------------------------------------------------------")
    self.mylog("Watching entities:")
    config = self.args["config"]
    self.mylog(config["entities"])
    try:
      if 'sqlitedb' in config:
        connection = sqlite3.connect(config["sqlitedb"])
      else:
        connection = pymysql.connect(host=f'{config["db"]["host"]}',
                                 port=int(f'{config["db"]["port"]}'),
                                 user=f'{config["db"]["user"]}',
                                 password=f'{config["db"]["password"]}',
                                 db=f'{config["db"]["db"]}',
                                 charset=f'{config["db"]["charset"]}',
                                 cursorclass=pymysql.cursors.DictCursor)
#    except pymysql.Error as err:
    except BaseException as err:
      self.mylog(f"Unexpected {method} {err=}, {type(err)=}")
      self.mylog("DB not connected ...")
      raise MySQLConnectionError
       
    self.mylog("DB connected ...")
    for entity in config["entities"]:
        #self.mylog(entity)
        self.check_entity(entity, connection)
    connection.close()

    runtime = datetime.time(0, 5, 0)
    self.run_hourly(self.run_ElectricConsumptionDbRepair, runtime)

  def run_ElectricConsumptionDbRepair(self, cb_args):
    config = self.args["config"]
    if 'sqlitedb' in config:
      connection = sqlite3.connect(config["sqlitedb"])
    else:
      connection = pymysql.connect(host=f'{config["db"]["host"]}',
                                 port=int(f'{config["db"]["port"]}'),
                                 user=f'{config["db"]["user"]}',
                                 password=f'{config["db"]["password"]}',
                                 db=f'{config["db"]["db"]}',
                                 charset=f'{config["db"]["charset"]}',
                                 cursorclass=pymysql.cursors.DictCursor)
    if config["every_hour_info"] == 1:
      self.mylog("I'm running every hour....")
    for entity in config["entities"]:
        self.check_entity(entity, connection)
    connection.close()
