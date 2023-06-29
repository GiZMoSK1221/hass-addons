Script tries to repair statistics, wrong received data from sensor. Typically when one value is too high and scrambles charts in energy dashboard

Script runs every hour and checks sum and state column in statistics table if new values for checked sensor are correct and repairs sum column.

example UPDATE statistics SET sum = sum - (168296.98-89.52) WHERE metadata_id = 36 AND sum > 89.52
and same to statistic_short_term table

Preconditions:
- appdaemon installed
- statistics data for all sensor are correct (script checks only new values)

Installation
1. add pymysql package to appdaemon config
python_packages:
  - pymysql
2. add log section to appdaemon.yaml
3. add ECDbRepair section to apps.yaml and configure it
4. copy ElectricConsumtionDbRepair.py to appdaemon\apps\ 
5. run
6. check electric_consumption_db_repair.log
	look for lines Watching entities:...  & DB connected ... 

Examples are in github


