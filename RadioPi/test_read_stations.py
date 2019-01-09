from radiostation.radio_browser_de_api_model import RadioBrowserDeClient
from radiostation.radioservice import RadioService
client = RadioBrowserDeClient()
service = RadioService(client)

stations = service.find_stations_by_topvote(5)

for station in stations:
    print(station.get_info())

countries = service.get_countries("deut")

for country in countries:
    print(country.get_info())
