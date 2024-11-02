# %%
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event
import json
import pandas as pd
import numpy as np

with open('../assets/times.json', 'r') as f:
    data = json.load(f)

data
# %%

# [{'month': 1,
#   'month_name': 'january',
#   'data': [{'day': 1,
#     'fajr': '6:58',
#     'sunrise': '8:50',
#     'dhuhr': '12:48',
#     'asr': '14:30',
#     'maghrib': '16:44',
#     'isha': '18:30'}, ...

# make an ical with every entry in +2 GMT

cal = Calendar()
cal.add('prodid', '-//My calendar product//mxm.dk//')
cal.add('version', '2.0')

time_zone = pytz.timezone('Europe/Amsterdam')

for month in data:
    if month['month'] < 11:
        continue
    for day in month['data']:
        for key, value in day.items():
            if key == 'day':
                continue
            event = Event()
            event.add('summary', key)
            event.add('dtstart',
                      datetime(2024,
                               month['month'],
                               day['day'],
                               int(value.split(":")[0]),
                               int(value.split(":")[1]),
                               0,
                               tzinfo=time_zone
                               ))
            event.add('dtend', datetime(2024, month['month'], day['day'], int(value.split(
                ":")[0]), int(value.split(":")[1]), 0, tzinfo=time_zone) + timedelta(minutes=5))
            cal.add_component(event)
for month in data:
    for day in month['data']:
        for key, value in day.items():
            if key == 'day':
                continue
            event = Event()
            event.add('summary', key)
            event.add('dtstart', datetime(2025, month['month'], day['day'], int(
                value.split(":")[0]), int(value.split(":")[1]), 0, tzinfo=time_zone))
            event.add('dtend', datetime(2025, month['month'], day['day'], int(value.split(
                ":")[0]), int(value.split(":")[1]), 0, tzinfo=time_zone) + timedelta(minutes=5))
            cal.add_component(event)

with open('../public/prayer_times.ics', 'wb') as f:
    f.write(cal.to_ical())

# %%
