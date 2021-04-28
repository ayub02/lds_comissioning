import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec


def list_files(_path, _extension):
    return [_file for _file in os.listdir(_path) if _file.endswith('.' + _extension)]


test_num = '9a'

sound_speed = 1062

test_times = {'1': '12:35:20', '2': '13:11:25', '3': '13:57:16', '4': '15:23:31', '5': '16:06:50', '6': '17:23:58',
              '6a': '17:24:10', '7': '17:26:59', '8': '17:44:55', '9': '18:01:00', '9a': '18:03:28'}


path = 'E:/INTECH/Projects/PARCO MFM/Comissioning/PrePOC leak test/NPW test {}/'.format(test_num)

files = list_files(path, 'csv')

num_subplots = len(files)
myFmt = mdates.DateFormatter('%H:%M:%S')
fig, ax = plt.subplots(num_subplots, 1)
fig.autofmt_xdate()

fig.subplots_adjust(hspace=0.05, wspace=0.005)
fig.suptitle('Test # ' + test_num)
for i, file in enumerate(files):
    if 'PT_62' in file:

        test_time = datetime.strptime('12/18/2020 ' + test_times[test_num], '%m/%d/%Y %H:%M:%S') \
                    + timedelta(seconds=22.361e3/sound_speed)
        print('PT_62: ', test_time)

    if 'PT_63' in file:
        test_time = datetime.strptime('12/18/2020 ' + test_times[test_num], '%m/%d/%Y %H:%M:%S')
        print('PT_63: ', test_time)

    if 'PT_64' in file:
        test_time = datetime.strptime('12/18/2020 ' + test_times[test_num], '%m/%d/%Y %H:%M:%S') \
                    + timedelta(seconds=421/sound_speed)
        print('PT_64: ', test_time)

    df = pd.read_csv(path+file, header=0)
    timestamps = []
    pVals = []
    for index, row in df.iterrows():
        timestamps.append(datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S.%f'))
        pVals.append(row[2])
    ax[i].plot(timestamps, pVals, marker='.', markeredgecolor='y')
    ax[i].axvline(x=test_time, linewidth=0.5, linestyle='--', color='olive')
    ax[i].xaxis.set_major_formatter(myFmt)
    ax[i].set_ylabel(file[10:15])
    # ax2 = ax[i].twinx()
    # ax2.axhline(y=0.5, linewidth=0.5, color='r', label='wow')
    plt.legend()

fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.95, wspace=0.005, hspace=0.1)
plt.show()
