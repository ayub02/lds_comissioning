import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import matplotlib.patches as patches
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.interpolate import interp1d


def gen_buffer_TS(_start, _sampling_rate, _buffer_len):
    _buffer_TS = [_start]
    for i in range(1, _buffer_len):
        _buffer_TS.append(_buffer_TS[i - 1] + timedelta(seconds=_sampling_rate / 1000))
    assert len(_buffer_TS) == _buffer_len
    return _buffer_TS


def analyze(_path_to_settings, _idx, _path_to_data):
    _data = pd.read_csv(_path_to_data, header=0)
    _data = _data.sort_values(by=['Seconds'])
    _data = _data.drop_duplicates(subset='Seconds', keep="first")
    _timestamps = []
    _seconds = []
    _pVals = []
    for index, _row in _data.iterrows():
        _timestamps.append(datetime.strptime(_row[0], '%m/%d/%Y %H:%M:%S.%f'))
        _seconds.append(_row[1])
        _pVals.append(_row[2])

    _df_orig = pd.DataFrame({'timestamps': _timestamps, 'seconds': _seconds, 'pVals': _pVals})
    _settings = pd.read_csv(_path_to_settings, header=0)
    _NUM_SAMPLES_1_AVG = _settings['NUM_SAMPLES_1_AVG'][_idx]
    _NUM_SAMPLES_2_AVG = _settings['NUM_SAMPLES_2_AVG'][_idx]
    _START_SAMPLE_2_AVG = _settings['START_SAMPLE_2_AVG'][_idx]
    _NPW_SAMPLE_BEFORE = _settings['NPW_SAMPLE_BEFORE'][_idx]
    _NPW_SAMPLE_AFTER = _settings['NPW_SAMPLE_AFTER'][_idx]
    _sampling_rate = _settings['sampling_rate'][_idx]
    _NPW_THR = _settings['NPW_THR'][_idx]

    _df_settings = pd.DataFrame({'NUM_SAMPLES_1_AVG': [_NUM_SAMPLES_1_AVG], 'NUM_SAMPLES_2_AVG': [_NUM_SAMPLES_2_AVG],
                                 'START_SAMPLE_2_AVG': [_START_SAMPLE_2_AVG], 'NPW_SAMPLE_BEFORE': [_NPW_SAMPLE_BEFORE],
                                 'NPW_SAMPLE_AFTER': [_NPW_SAMPLE_AFTER], 'sampling_rate': [_sampling_rate],
                                 'NPW_THR': [_NPW_THR]})

    print('NUM_SAMPLES_1_AVG \t\t', _NUM_SAMPLES_1_AVG)
    print('NUM_SAMPLES_2_AVG \t\t', _NUM_SAMPLES_2_AVG)
    print('START_SAMPLE_2_AVG \t\t', _START_SAMPLE_2_AVG)
    print('NPW_SAMPLE_BEFORE \t\t', _NPW_SAMPLE_BEFORE)
    print('NPW_SAMPLE_AFTER \t\t', _NPW_SAMPLE_AFTER)
    print('sampling_rate \t\t\t', _sampling_rate)
    print('NPW_THR \t\t\t\t', _NPW_THR)
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
        _pVals_new.append(f(t).item())
    assert len(_pVals_new) == len(_timestamps_new)

    _df_interp = pd.DataFrame({'timestamps_new': _timestamps_new, 'seconds_new': _seconds_new, 'pVals_new': _pVals_new})

    ###################################################################################################################
    # Calculating difference of averages
    ###################################################################################################################
    wave = _pVals_new
    queue = []
    _NPW_THR_break = []
    _Buffer_start = []
    _Buffer_end = []
    _Buffer = []
    _diff = np.zeros(len(wave))
    detected = False
    results = []
    queue_len = _START_SAMPLE_2_AVG + _NUM_SAMPLES_2_AVG
    counter = 0
    for i in range(len(wave)):
        _val = wave[i]
        if len(queue) >= queue_len:
            queue.pop(0)
        queue.append(_val)

        assert len(queue) <= queue_len

        if len(queue) == queue_len:
            avg1 = np.average(queue[-_NUM_SAMPLES_1_AVG:])
            avg2 = np.average(queue[-(_NUM_SAMPLES_2_AVG + _START_SAMPLE_2_AVG):-_START_SAMPLE_2_AVG])
            _diff[i] = avg1 - avg2

            if _diff[i] <= _NPW_THR and not detected and counter == 0:
                results.append(i)
                detected = True
                _NPW_THR_break.append(_timestamps_new[i])
                _Buffer_start.append(
                    _timestamps_new[i] + timedelta(seconds=-_NPW_SAMPLE_BEFORE * _sampling_rate / 1000))
                _Buffer_end.append(
                    _timestamps_new[i] + timedelta(seconds=_NPW_SAMPLE_AFTER * _sampling_rate / 1000))
                _Buffer.append(wave[i-_NPW_SAMPLE_BEFORE:i+_NPW_SAMPLE_AFTER])
                counter = _NPW_SAMPLE_AFTER

            if counter > 0:
                counter -= 1

            if _diff[i] > _NPW_THR:
                detected = False

    _df_interp['Diff_of_avgs'] = _diff
    _df_results = pd.DataFrame({'NPW_THR_break': _NPW_THR_break, 'Buffer_start': _Buffer_start, 'Buffer_end': _Buffer_end, 'Buffer': _Buffer})
    return _df_orig, _df_interp, _df_settings, _df_results


path_to_settings = 'E:\INTECH\Projects\PARCO MFM\ldsTesting\data\Edge_device_settings.csv'
# path_to_data = 'E:\INTECH\Projects\PARCO MFM\Comissioning\PrePOC leak test/NPW test 8\MQTT_BV62_PT_62__from__2020_12_18__17_25__to__2020_12_18__17_55.csv'
path_to_data = 'E:\INTECH\Projects\PARCO MFM\ldsTesting\data\MQTT_BV64_PT_64__from__2020_12_18__12_00__to__2020_12_18__18_20.csv'

leak_times_64 = ['12:35:20', '13:11:24', '13:57:16', '15:23:30', '16:06:57', '17:23:58', '17:27:01', '17:44:53',
                 '18:01:00', '18:03:28']
df_orig, df_interp, df_settings, df_results = analyze(path_to_settings, 2, path_to_data)

for val in df_results['NPW_THR_break']:
    print(val)

myFmt = mdates.DateFormatter('%H:%M:%S')
fig, ax = plt.subplots(2, 1)
fig.autofmt_xdate()
ax[0].plot(df_orig['timestamps'], df_orig['pVals'], marker='.', markeredgecolor='olive')
for _, row in df_results.iterrows():
    ax[0].plot(gen_buffer_TS(row[1], df_settings['sampling_rate'][0], len(row[3])), row[3], 'y')
# [ax[0].axvline(x=_x, linewidth=0.5, linestyle='--', color='olive') for _x in df_results['NPW_THR_break']]
[ax[0].axvline(x=datetime.strptime('12/18/2020 ' + _x, '%m/%d/%Y %H:%M:%S'), linewidth=0.5, linestyle=':', color='black') for _x in leak_times_64]
ax[0].xaxis.set_major_formatter(myFmt)

ax[1].plot(df_interp['timestamps_new'], df_interp['Diff_of_avgs'])
ax[1].axhline(y=df_settings['NPW_THR'][0], linewidth=0.5, color='red')
[ax[1].axvline(x=_x, linewidth=0.5, linestyle='--', color='olive') for _x in df_results['NPW_THR_break']]

ax[1].set_ylim(-0.2, 0.2)
ax[1].xaxis.set_major_formatter(myFmt)

plt.show()



