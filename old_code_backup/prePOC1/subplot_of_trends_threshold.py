import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d


def list_files(_path, _extension):
    return [_file for _file in os.listdir(_path) if _file.endswith('.' + _extension)]


def get_settings(_settings):
    if _settings == 'Actual':
        _NUM_SAMPLES_1_AVG = 150
        _NUM_SAMPLES_2_AVG = 200
        _START_SAMPLE_2_AVG = 10000
        _NPW_THR = 0.05
        _NPW_SAMPLE_BEFORE = 150
        _NPW_SAMPLE_AFTER = 350
        _sampling_rate = 20
        return _NUM_SAMPLES_1_AVG, _NUM_SAMPLES_2_AVG, _START_SAMPLE_2_AVG, _NPW_THR, _NPW_SAMPLE_BEFORE, \
               _NPW_SAMPLE_AFTER, _sampling_rate

    if _settings == 'PSI':
        _NUM_SAMPLES_1_AVG = 150
        _NUM_SAMPLES_2_AVG = 1000
        _START_SAMPLE_2_AVG = 250
        _NPW_THR = 0.05
        _NPW_SAMPLE_BEFORE = 150
        _NPW_SAMPLE_AFTER = 350
        _sampling_rate = 50
        return _NUM_SAMPLES_1_AVG, _NUM_SAMPLES_2_AVG, _START_SAMPLE_2_AVG, _NPW_THR, _NPW_SAMPLE_BEFORE, \
               _NPW_SAMPLE_AFTER, _sampling_rate


def get_diff(_settings, _timestamps, _seconds, _pVals):
    NUM_SAMPLES_1_AVG, NUM_SAMPLES_2_AVG, START_SAMPLE_2_AVG, NPW_THR, NPW_SAMPLE_BEFORE, NPW_SAMPLE_AFTER, \
    _sampling_rate = get_settings(_settings)
    ###################################################################################################################
    # Interpolating
    ###################################################################################################################
    f = interp1d(_seconds, _pVals, kind='linear')
    assert _seconds[0] == 0
    assert _seconds[-1] > _seconds[0]

    _seconds_new = np.arange(0, int(np.floor(_seconds[-1])), _sampling_rate / 1000)
    _pVals_new = []
    _timestamps_new = []
    for idx, t in enumerate(_seconds_new):
        if idx == 0:
            _timestamps_new.append(_timestamps[0])
        else:
            _timestamps_new.append(_timestamps_new[idx - 1] + timedelta(seconds=_sampling_rate / 1000))
        _pVals_new.append(f(t))
    assert len(_pVals_new) == len(_timestamps_new)

    ###################################################################################################################
    # Calculating difference of averages
    ###################################################################################################################
    wave = _pVals_new
    queue = []
    _NPW_THR_break = []
    _diff = np.zeros(len(wave))
    detected = False
    results = []
    queue_len = START_SAMPLE_2_AVG + NUM_SAMPLES_2_AVG
    for i in range(len(wave)):
        val = wave[i]
        if len(queue) >= queue_len:
            queue.pop(0)
        queue.append(val)

        if len(queue) == queue_len:
            avg1 = np.average(queue[-NUM_SAMPLES_1_AVG:])
            avg2 = np.average(queue[-(NUM_SAMPLES_2_AVG + START_SAMPLE_2_AVG):-START_SAMPLE_2_AVG])
            _diff[i] = abs(avg1 - avg2)
            if _diff[i] < 0:
                _diff[i] = 0
            # if abs(avg1 - avg2) >= NPW_THR:
            #     _diff[i] = NPW_THR * 1.5

            if abs(avg1 - avg2) >= NPW_THR and not detected:
                results.append(i)
                detected = True
                _NPW_THR_break.append(i)
            if abs(avg1 - avg2) < NPW_THR:
                detected = False

    return _diff, _NPW_THR_break, NPW_THR, _seconds_new


test_num = '1'
sound_speed = 1062

test_times = {'1': '12:35:20', '2': '13:11:25', '3': '13:57:16', '4': '15:23:31', '5': '16:06:50', '6': '17:23:58',
              '7': '17:26:59', '8': '17:44:55', '9': '18:01:00', '9a': '18:03:28'}

path = 'E:/INTECH/Projects/PARCO MFM/Comissioning/PrePOC leak test/NPW test {}/'.format(test_num)

files = list_files(path, 'csv')

num_subplots = len(files)
myFmt = mdates.DateFormatter('%H:%M:%S')
fig, ax = plt.subplots(num_subplots, 1)
fig.autofmt_xdate()
fig.subplots_adjust(hspace=0.05, wspace=0.005)
fig.suptitle('Test # ' + test_num)
for _file_num, file in enumerate(files):
    if 'PT_62' in file:
        test_time = datetime.strptime('12/18/2020 ' + test_times[test_num], '%m/%d/%Y %H:%M:%S') \
                    + timedelta(seconds=22.361e3 / sound_speed)
        print('PT_62: ', test_time)

    if 'PT_63' in file:
        test_time = datetime.strptime('12/18/2020 ' + test_times[test_num], '%m/%d/%Y %H:%M:%S')
        print('PT_63: ', test_time)

    if 'PT_64' in file:
        test_time = datetime.strptime('12/18/2020 ' + test_times[test_num], '%m/%d/%Y %H:%M:%S') \
                    + timedelta(seconds=421 / sound_speed)
        print('PT_64: ', test_time)

    df = pd.read_csv(path + file, header=0)
    df = df.sort_values(by=['Seconds'])
    df = df.drop_duplicates(subset='Seconds', keep="first")
    timestamps = []
    seconds = []
    pVals = []
    for index, row in df.iterrows():
        timestamps.append(datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S.%f'))
        seconds.append(row[1])
        pVals.append(row[2])

    ###################################################################################################################
    # Computing difference and plotting
    ###################################################################################################################
    ax1 = ax[_file_num]
    ax1.plot(seconds, pVals, markersize=2, marker='.', markeredgecolor='y', label='Pressure values (periodic)')
    ax1.axvline(x=(test_time - timestamps[0]).total_seconds(), linewidth=1, linestyle='--', color='olive',
                label='Time of leak')
    ax1.set_ylabel(file[10:15] + '\nbar')

    ax2 = ax1.twinx()
    settings = 'Actual'
    diff, NPW_THR_break, NPW_THR_returned, seconds_new = get_diff(settings, timestamps, seconds, pVals)
    ax2.axhline(y=NPW_THR_returned, linewidth=0.5, color='r', label='Threshold')
    ax2.plot(seconds_new, diff, linestyle='-.', linewidth=0.5, label='Abs diff of avg on ' + settings + ' settings')
    ax2.set_ylabel('bar')

    settings = 'PSI'
    diff, NPW_THR_break, NPW_THR_returned, seconds_new = get_diff(settings, timestamps, seconds, pVals)
    ax2.plot(seconds_new, diff, linestyle='--', linewidth=0.5, label='Abs diff of avg on ' + settings + ' settings')
    # ax1.set_xlim(1000, 1500)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

fig.subplots_adjust(left=0.07, bottom=0.1, right=0.95, top=0.95, wspace=0.005, hspace=0.1)
plt.show()
