import vk_api
import json
import configparser

cfg = configparser.ConfigParser()
cfg.read('./config/config.cfg')
accounts = json.loads(cfg['ACCOUNTS']['bots'])

vk_client = vk_api.VkApi(
    token=list(accounts[0].values())[0])
client = vk_client.get_api()

# Get country id here
print(client.database.getCountries(code='RU'))
# Get city id here
print(client.database.getCities(country_id=1, q='Москва'))
