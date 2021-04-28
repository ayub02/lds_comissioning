import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from scipy.interpolate import interp1d


# std dev = 0.014392293

path = 'E:\INTECH\Projects\PARCO MFM\ldsTesting\output\For fahad/'
from_file = 'MQTT_BV64_PT_64__from__2020_12_18__09_11__to__2020_12_18__18_11'

do_plot = True
do_export = True

df = pd.read_csv(path+from_file+'.csv', header=0)

timestamps_raw = df['Timestamps'].to_list()
time = df['Seconds'].to_list()
val = df['Values'].to_list()

sampling_rate = 20                          # msec

f = interp1d(time, val, kind='linear')
assert time[0] == 0
assert time[-1] > time[0]

timestamps = []
timestamps_new = []
time_new = np.arange(0, int(np.floor(time[-1])), sampling_rate/1000)
val_new = []

for _t in timestamps_raw:
    timestamps.append(datetime.strptime(_t, '%m/%d/%Y %H:%M:%S.%f'))

for idx, t in enumerate(time_new):
    if idx == 0:
        timestamps_new.append(datetime.strptime(timestamps_raw[0], '%m/%d/%Y %H:%M:%S.%f'))
    else:
        timestamps_new.append(timestamps_new[idx - 1] + timedelta(seconds=sampling_rate / 1000))
    val_new.append(f(t) + np.random.normal(loc=0.0, scale=0.0144))


myFmt = mdates.DateFormatter('%H:%M:%S')
fig, ax = plt.subplots(1, 1)
fig.autofmt_xdate()
ax.plot(timestamps_new, val_new)
ax.plot(timestamps, val, '--')
ax.xaxis.set_major_formatter(myFmt)
plt.show()

if do_export:
    to_file = from_file+'____'+str(sampling_rate)+'msec'

    df_new = pd.DataFrame(list(zip(timestamps_new, time_new, val_new)), columns=['Timestamps', 'Seconds', 'Values'])
    if os.path.exists(path+to_file+'.csv'):
        os.remove(path+to_file+'.csv')
        print('Removed ', to_file+'.csv')
    else:
        df_new.to_csv(path+to_file+'.csv', index=False)
        print('File write successful \t\t', to_file+'.csv')

