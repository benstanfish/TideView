from datetime import datetime, timedelta
import urllib.request
import json
from typing import Dict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import pandas as pd

stations: Dict = {
    'henderson inlet': '9446752',
    'tacoma': '9446484',
    'tacoma narrows': '9446486',
    'gig harbor': '9446369',
    'yoman point': '9446705',
    'budd inlet': '9446807'
}
station = 'yoman point'

product = 'predictions'
time_type = 'lst_ldt'
data_units = 'metric'
data_format = 'json'
begin_date = datetime.now().strftime('%Y%m%d')
days_ahead = 0
end_date = (datetime.today() + timedelta(days=days_ahead)).strftime('%Y%m%d')

datum = 'MLLW'

api_url = f'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={begin_date}&end_date={end_date}&station={stations[station]}&product={product}&datum={datum}&time_zone={time_type}&units={data_units}&format={data_format}'


def get_data(api_url: str=api_url) -> Dict:
    try:
        with urllib.request.urlopen(api_url) as url:
            data = json.load(url)
            return data
    except Exception as e:
        print(e)
    return {}

predictions = get_data(api_url)['predictions']

times = []
heights = []

for dictionary in predictions:
    for key, value in dictionary.items():
        if key == 't':
            times.append(datetime.strptime(value, '%Y-%m-%d %H:%M'))
        else:
            heights.append(float(value))

plt.plot(times, heights)
ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.xlabel('Time (Today)')
plt.ylabel('Height (m)')
plt.grid(True)
plt.title(f'Tide Predictions for {station.title()}')
plt.show()