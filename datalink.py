from datetime import datetime, timedelta
import urllib.request
import json
from typing import Dict
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np
from scipy.signal import find_peaks
# import pandas as pd

stations: Dict = {
    'henderson inlet': '9446752',
    'tacoma': '9446484',
    'tacoma narrows': '9446486',
    'gig harbor': '9446369',
    'yoman point': '9446705',
    'budd inlet': '9446807'
}
station = 'tacoma'

product = 'predictions'
time_type = 'lst_ldt'
data_units = 'english' # metric or english
units = 'ft'
if data_units == 'metric':
    units = 'm'
data_format = 'json'
days_behind = 0
begin_date = (datetime.now() - timedelta(days=days_behind)).strftime('%Y%m%d')
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



# peaks, _ = find_peaks(np.array(heights))
# print([heights[peak] for peak in peaks])

# valleys, _ = find_peaks(-np.array(heights))
# print([heights[valley] for valley in valleys])

# for i, height in enumerate(heights):
#     print(i, height)

asc_ht = []
asc_time = []
desc_ht = []
desc_time = []

for i in range(len(heights) - 1):
    change = heights[i + 1] - heights[i]
    # print(i, change, change < 0)
    if change < 0:
        desc_ht.append(heights[i])
        desc_time.append(times[i])
        asc_ht.append(np.nan)
        asc_time.append(times[i])
    else:
        desc_ht.append(np.nan)
        desc_time.append(times[i])
        asc_ht.append(heights[i])
        asc_time.append(times[i])

plt.plot(times, [3.25]*len(times), color='slategray')
plt.plot(times, heights, color='dodgerblue')
plt.plot(desc_time, desc_ht, color='orangered')
plt.fill_between(desc_time, desc_ht, 3.25, color='lightblue', alpha=0.5)
plt.fill_between(asc_time, asc_ht, 3.25, color='lightblue', alpha=1)

# TODO: need to determine the time in the location of the data, not the compiler.
time_now = datetime.now()
nearest_time = times.index(min(times, key=lambda x: abs(x - time_now)))
height_now = heights[nearest_time]

plt.axvline(x=time_now, 
            ymin=0, ymax=1,
            color='darkslategray', 
            linestyle='--', 
            label='now')

# plt.text(time_now, height_now, f'Current tide\n{height_now} ({units})', fontsize=11, color='slategray')

plt.plot(time_now, height_now, marker='o', color='darkslategray')
plt.annotate(
    f'Current tide\n{height_now} ({units})',
    xy=(time_now, height_now),
    xytext=(time_now + timedelta(minutes=30), height_now + 0.25),
    fontsize=11,
    color='darkslategray'
)

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
ax.xaxis.set_minor_locator(mdates.HourLocator(np.arange(0,24,6)))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H'))
plt.xlabel('Date and Time')
plt.ylabel(f'Height ({units})')
plt.grid(True)
plt.title(f'Tide Predictions for {station.title()}')
plt.show()