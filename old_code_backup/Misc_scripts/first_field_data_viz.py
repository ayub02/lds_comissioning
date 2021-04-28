from numpy import genfromtxt
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
from numpy.fft import fft, fftfreq


def decode_time(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    if _buffer[0] >= 90:
        year = '19' + hex(_buffer[0])[2:]
    else:
        year = '20' + hex(_buffer[0])[2:]
    month = hex(_buffer[1])[2:]
    day = hex(_buffer[2])[2:]
    hour = hex(_buffer[3])[2:]
    minute = hex(_buffer[4])[2:]
    second = hex(_buffer[5])[2:]
    millisecond = hex(_buffer[6])[2:] + hex(_buffer[7])[2]
    # datetime(year, month, day, hour, minute, second, microsecond)
    try:
        datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(millisecond))
    except:
        return 'Invalid Timestamp'
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(millisecond))


def decode(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    _pVal = []
    for i in range(8, _buffer_len, 2):
        _pVal.append((_buffer[i] << 8) + _buffer[i + 1])
    return _pVal


my_data = genfromtxt('../data/BV62TestFlags.csv', delimiter=',')
fft_results = []
for row in my_data:
    buffer = [int(val) for val in row]
    values = [val/500 for val in decode(1008, buffer)]
    print(round(np.std(values), 4))
    plt.plot(values, label='BV61.NPW.ByteArray     ' + 'Buffer TS:' +decode_time(1008, buffer).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    plt.legend(bbox_to_anchor=(1, 1.16), fontsize='x-small')

plt.show()
