## Home Assistant Wattsonic GEN3 MODBUS integration

**Installation**:
1. edit configuration.yaml
include packages according to minimal/complete installation, check my [configuration.yaml](configuration.yaml)

2. copy wattsonic files
all files copy to your config dir (where is configuration.yaml)

	a) **minimal Wattsonic gen3** configuration
		start with this config. When your setup starts returning data, switch to latest configuration. minimal config has almost all sensors from modbus + 3 translated template sensor
		- copy just this older [wattsonic.yaml](https://raw.githubusercontent.com/GiZMoSK1221/hass-addons/7c4f86199650526064935fac353a233ae6daa0ea/wattsonic/wattsonic.yaml) 
		

	b) **my latest gen3** configuration
		- copy [wattsonic_sql_postgre.yaml](wattsonic_sql_postgre.yaml) or [wattsonic_sql_mariadb.yaml](wattsonic_sql_mariadb.yaml) for sql sensors according to your db. Default HA is postgre
		- copy actual [wattsonic.yaml](wattsonic.yaml)
	
	this configuration consist of (but still does not has all registers):
	- almost all read modbus registers
	- switches for RW registers
	- can read Ecomode period 1,2 structure and has an example for writing structure
	- template sensors
		- Battery SOC ETA - time for charging/discharging battery
		- Grid Injection 15min - for Czech, grid injection in last 15minutes
		- Home Consumption Now and Today calculation
	- scripts for
		- setting economy/general/off grid mode
		- setting Grid Injection Power Limit Setting
	
	c) **GEN2** configuration
	as GEN2 has differrent registers, you cannot use my wattsonic.yaml.
	but, Ivan has made this basic one [wattsonic_gen2.yaml](wattsonic_gen2.yaml). enjoy and feel free to modify here on github

4. edit modbus configuration in wattsonic.yaml
		 default is connection over serial and RS485. Change port according to your RS485 module.
		 if you are running over TCP/IP, just delete serial config and uncomment tcp config

5. restart HASS
6. edit your lovelace dashboard, you can take mine [lovelace](lovelace.yaml) and just remove/use sensors


**MODBUS wiring GEN3**
check [wattsonic manual](https://www.wattsonic.com/Ftp/EN/Wattsonic%20Li-HV%20Residential%20Three%20Phase%20Hybrid%20Series_UM_EN.pdf), page 65, PIN 13,14

**MODBUS wiring GEN2**
 Sunways manual for STH 3~8KTL-HS, page 49, PIN 3,4

**RS485 converter**
i'm using this [converter](https://www.aliexpress.com/item/1005003207091292.html)

**Questions:**
place here: [Hass community forum](https://community.home-assistant.io/t/wattsonic-photovoltaic-power-plant-fve-integration/406135) 
