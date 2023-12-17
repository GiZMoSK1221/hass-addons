## PID tabule

Script kazdu minutu stiahne pozadovane odchody a posle ich do HA
zdroj dat: golemio API

![][https://github.com/GiZMoSK1221/hass-addons/blob/main/PIDtabule/priklad.png]

**Preconditions:**
- vlastny token z [golemio](https://api.golemio.cz/api-keys/auth/sign-in)
- je potrebny HA addon Appdaemon
- zobrazenie je cez flexCards https://github.com/custom-cards/flex-table-card

**Instalacia**
1. ak chcete logovat do extra suboru, pridajte potrebnu sekciu do addon_configs\axx_appdaemon\ [appdaemon.yaml](appdaemon.yaml)
2. pridajte sekciu PIDtabule do addon_configs\axx_appdaemon\apps\ [apps.yaml](apps.yaml)
3. nakopirujte [PIDtabule.py](pidtabule.py) do addon_configs\axx_appdaemon\apps
4. script vytvori entitu sensor.PIDtabule
json s odchodmi je v atribute data
state entity je este v designe + dalsie atributy alebo entity

**Priklad:**
- [flexcard.yaml](flexcard.yaml)
- [markdown.yaml](markdown.yaml)
