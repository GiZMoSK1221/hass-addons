<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->


## 0.9.8
Changes reflecting new config storage for addons according to: https://developers.home-assistant.io/blog/2023/11/06/public-addon-config/

Until now, the configs (stations.yaml and netatmo_token.yaml) were stored in /config/nwfs/ directory.

New storage will be /addon-config/slug_nfws/

After update, during first run, when addon detects both config files in old storage, it will copy them to the new storage. When everyting goes well, addon will start and continue working. Then you can delete the old directory.

If migrations fails, try to copy files manually. Otherwise follow instructions in Troubleshooting section in [docs.md](https://github.com/GiZMoSK1221/hass-addons/blob/main/nfws/DOCS.md)
