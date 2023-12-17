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

  def check_entity_test(self, entity, connection):
    config = self.args["config"]
    cursor = connection.cursor()
    #sql = f"""SELECT sst.id as id, sst.metadata_id, sst.state, sst.sum, sst.created_ts FROM statistics sst LIMIT 1"""
    sql = f"""SELECT sm.id FROM statistics_meta sm where sm.statistic_id='{entity}'"""
    cursor.execute(sql)
    result_id = cursor.fetchone()
    #self.mylog(result_id)
    if result_id == None:
        self.mylog(f"Entity not found: {entity}" )
        return
    if 'sqlitedb' in config:
      result_id = {
        "id": result_id[0]
        }
    sm_id = result_id["id"]
    #self.mylog(sm_id)
    #return
    sql = f"""SELECT sst.id as id, sst.metadata_id, sst.state, sst.sum, '{entity}' as statistic_id, sst.created_ts FROM statistics sst 
             where sst.metadata_id ={sm_id}
             order by sst.start_ts desc limit 1"""
    #self.mylog(sql)
    cursor.execute(sql)
    result_last = cursor.fetchone()
    #self.mylog(result_last)
    if result_last == None:
        self.mylog(f"No data found: {entity}" )
        return


  def check_entity(self, entity, connection):
    config = self.args["config"]
    cursor = connection.cursor()
    sql = f"""SELECT sst.id as id, sst.metadata_id, sst.state, sst.sum, sm.statistic_id, sst.start_ts FROM statistics sst 
             inner join statistics_meta sm on sm.id=sst.metadata_id and sm.statistic_id='{entity}' 
             order by sst.start_ts desc LIMIT 1"""
    #self.mylog( "c1 start" )
    cursor.execute(sql)
    #self.mylog( "c1 stop" )
    result_last = cursor.fetchone()
    #self.mylog(result_last)
    sql = f"""select id, metadata_id, state, sum, statistic_id, start_ts from 
            (SELECT sst.id as id, sst.metadata_id, sst.state, sst.sum, sm.statistic_id, sst.start_ts, sst.start_ts FROM statistics sst 
             inner join statistics_meta sm on sm.id=sst.metadata_id and sm.statistic_id='{entity}'
             order by start_ts desc LIMIT 2) two 
            order by start_ts ASC limit 1"""
    #self.mylog( "c2 start" )
    cursor.execute(sql)
    #self.mylog( "c2 stop" )
    result_prev = cursor.fetchone()
    if result_last == None or result_prev == None:
        self.mylog(f"No data found: {entity}" )
        return

    if 'sqlitedb' in config:
      result_last = {
        "id": result_last[0],
        "metadata_id": result_last[1],
        "state": result_last[2],
        "sum": result_last[3],
        "statistic_id": result_last[4],
        "start_ts": result_last[5]
      }
      result_prev = {
        "id": result_prev[0],
        "metadata_id": result_prev[1],
        "state": result_prev[2],
        "sum": result_prev[3],
        "statistic_id": result_prev[4],
        "start_ts": result_prev[5]
      }

    dt_object = datetime.datetime.fromtimestamp(result_last['start_ts'])
    sum_diff = result_last['sum']-result_prev['sum']
    state_diff = result_last['state']-result_prev['state']
#    if sum_diff > state_diff+1:
    if abs(sum_diff - state_diff) > 0.3:
      if result_last['state']<result_prev['state']:
        self.mylog(f"{dt_object} {entity} newer is lower")
        self.mylog(result_prev)
        self.mylog(result_last)
        new_sum = result_prev['sum']-result_prev['state']+result_last['state']
        update_s =              f"""UPDATE statistics SET sum = {new_sum}, state = {result_last['state']} WHERE metadata_id = {result_last['metadata_id']} AND start_ts >= {result_prev['start_ts']};"""
        update_sst = f"""UPDATE statistics_short_term SET sum = {new_sum}, state = {result_last['state']} WHERE metadata_id = {result_last['metadata_id']} AND start_ts >= {result_prev['start_ts']};"""
        self.mylog(update_s)
        self.mylog(update_sst)
      else:
        self.mylog(f"{dt_object} {entity} not ok")
        self.mylog(result_prev)
        self.mylog(result_last)
        update_s =              f"""UPDATE statistics SET sum = {result_prev['sum']}, state = {result_prev['state']} WHERE metadata_id = {result_last['metadata_id']} AND start_ts > {result_prev['start_ts']};"""
        update_sst = f"""UPDATE statistics_short_term SET sum = {result_prev['sum']}, state = {result_prev['state']} WHERE metadata_id = {result_last['metadata_id']} AND start_ts > {result_prev['start_ts']};"""
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
            cursor.close()
        except MySQLError as e:
            self.mylog(f"{e} -- {e.args[0]}")
    # elif result_last['state']<result_prev['state']:
        # self.mylog(f"{dt_object} {entity} newer is lower")
        # self.mylog(result_prev)
        # self.mylog(result_last)


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
        #self.mylog(entity)                 #logovanie spracovania sensoru, len pri initialize
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
