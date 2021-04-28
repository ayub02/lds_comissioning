import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


def bcd(val):
    res = val % 100   # we can BCD encode only two digits in one byte
    res = int(res/10) * 0x10 + res % 10
    return int(res)


# Creates an an array of 8-byte values to represent timestamp buffer as described above
def createTimeBuffer(t1):
    timeBuffer = [bcd(t1.year - 2000), bcd(t1.month), bcd(t1.day),
                  bcd(t1.hour), bcd(t1.minute), bcd(t1.second),
                  bcd(int(t1.microsecond / 10000)),
                  bcd((int((t1.microsecond - int(t1.microsecond / 10000) * 10000) / 1000) * 10)) + (
                      [2, 3, 4, 5, 6, 7, 1][t1.weekday()])]
    return timeBuffer


# generates a buffer with 200 hypothetical 2-byte pressure values
def createDataBuffer(original2byteDataArray):
    dataBuffer = []
    for x in original2byteDataArray:
        dataBuffer += [(x / 256) % 256, x % 256]
    return dataBuffer


def convertToJsonArray(_topic, completeDataBuffer):
    _myStr = """{"":[""" + ','.join(str(int(x)) for x in completeDataBuffer) + "]}"
    return _myStr[:2]+json_map[_topic]+_myStr[2:]


def gen_buffer_TS(_start, _sampling_rate, _buffer_len):
    _buffer_TS = [_start]
    for i in range(1, _buffer_len):
        _buffer_TS.append(_buffer_TS[i - 1] + timedelta(seconds=_sampling_rate / 1000))
    assert len(_buffer_TS) == _buffer_len
    return _buffer_TS


def analyze(_path_to_settings, _idx, _path_to_data):
    ###################################################################################################################
    # Get data
    ###################################################################################################################
    _df_orig = pd.read_csv(_path_to_data, header=0)
    _timestamps_new = _df_orig['Timestamps'].to_list()
    _pVals_new = _df_orig['Values'].to_list()

    _timestamps_new = []
    for val in _df_orig['Timestamps'].to_list():
        _timestamps_new.append(datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f'))
        # _timestamps_new.append(datetime.strptime(val, '%m/%d/%Y %H:%M:%S.%f'))
    _df_interp = pd.DataFrame({'Timestamps': _timestamps_new, 'Values': _pVals_new})

    ###################################################################################################################
    # Get settings
    ###################################################################################################################
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
    # Calculating difference of averages
    ###################################################################################################################
    wave = _pVals_new
    queue = []
    _NPW_THR_break = []
    _Buffer_start = []
    _Buffer_end = []
    _Buffer = []
    _threshold_break_index = []
    _diff = np.zeros(len(wave))
    _detected = np.zeros(len(wave), dtype=bool)
    detected = False
    _results = []
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
            _diff[i] = round(avg1, 3) - round(avg2, 3)
            _diff[i] = avg1 - avg2
            _detected[i] = detected
            if _diff[i] < _NPW_THR and not detected and counter == 0:
                _results.append(i)
                detected = True
                _NPW_THR_break.append(_timestamps_new[i])
                _Buffer_start.append(
                    _timestamps_new[i] + timedelta(seconds=-_NPW_SAMPLE_BEFORE * _sampling_rate / 1000))
                _Buffer_end.append(
                    _timestamps_new[i] + timedelta(seconds=_NPW_SAMPLE_AFTER * _sampling_rate / 1000))
                _Buffer.append(wave[i-_NPW_SAMPLE_BEFORE:i+_NPW_SAMPLE_AFTER])
                counter = _NPW_SAMPLE_AFTER+_NPW_SAMPLE_BEFORE

            if counter > 0:
                counter -= 1

            if _diff[i] > _NPW_THR:
                detected = False

    _df_interp['Diff_of_avgs'] = _diff
    _df_interp['Detected'] = _detected
    assert len(_diff) == len(_timestamps_new)

    _df_results = pd.DataFrame({'NPW_THR_break': _NPW_THR_break, 'Buffer_start': _Buffer_start, 'Buffer_end': _Buffer_end,
                                'Buffer': _Buffer, 'Threshold_break_index': _results})
    return _df_orig, _df_interp, _df_settings, _df_results


json_map = {'MKT': 'NPW_array_PT_2003', 'MOV60': 'NPW_array_PT_2084', 'BV61': 'NPW_array_PT_61',
                    'BV62': 'NPW_array_PT_62', 'BV63': 'NPW_array_PT_63', 'BV64': 'NPW_array_PT_64',
                    'BV65': 'NPW_array_PT_65', 'BV66': 'NPW_array_PT_66', 'MOV67': 'NPW_array_PT_3010',
                    'KBS': 'NPW_array_PT_3025'}

path_to_settings = '..\data\Edge_device_settings.csv'
path_to_data = '.\MQTT_BV64_PT_64__from__2020_12_18__09_11__to__2020_12_18__18_11____20msec.csv'

df_orig, df_interp, df_settings, df_results = analyze(path_to_settings, 1, path_to_data)

# for val in df_results['NPW_THR_break']:
#     print(val)

myFmt = mdates.DateFormatter('%H:%M:%S.%f')
fig, ax = plt.subplots(2, 1)

fig.autofmt_xdate()
ax[0].plot(df_interp['Timestamps'], df_interp['Values'])
ax[0].set_ylabel('Pressure (bar)')
ax[0].set_title('Dataset 1')
for _, row in df_results.iterrows():
    ax[0].plot(gen_buffer_TS(row[1], df_settings['sampling_rate'][0], len(row[3])), row[3], 'y')
ax[0].xaxis.set_major_formatter(myFmt)

ax[1].plot(df_interp['Timestamps'], df_interp['Diff_of_avgs'])
ax[1].axhline(y=df_settings['NPW_THR'][0], linewidth=0.5, color='red', label='Threshold')
[ax[1].axvline(x=_x, linewidth=0.5, linestyle='--', color='olive') for _x in df_results['NPW_THR_break']]
ax[1].set_ylabel('Difference of avg (bar)')
ax[1].legend()
ax[1].xaxis.set_major_formatter(myFmt)

# ax[2].plot(df_interp['Timestamps'], df_interp['Detected'])
# ax[2].xaxis.set_major_formatter(myFmt)

for _, row in df_results.iterrows():
    print(row[4], '\t', row[1], '\t', convertToJsonArray('MOV60', createTimeBuffer(row[1]) + createDataBuffer([val*500 for val in row[3]])))

plt.show()



