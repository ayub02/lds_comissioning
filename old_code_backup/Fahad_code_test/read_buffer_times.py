import json
from datetime import datetime, timedelta
from matplotlib import pyplot as plt


def decode(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    _pVal = []
    for i in range(8, _buffer_len, 2):
        _pVal.append(((_buffer[i] << 8) + _buffer[i + 1])/500)
    return _pVal

def decode_time(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    hour_offset = 0  # Hour offset implemented!!!
    if _buffer[0] >= 90:
        year = '19' + hex(_buffer[0])[2:]
    else:
        year = '20' + hex(_buffer[0])[2:]

    month = hex(_buffer[1])[2:]
    day = hex(_buffer[2])[2:]
    hour = int(hex(_buffer[3])[2:])
    minute = hex(_buffer[4])[2:]
    second = hex(_buffer[5])[2:]
    millisecond = hex(_buffer[6])[2:] + hex(int(_buffer[7] / 16))[2]

    try:
        _timestamp = datetime(int(year), int(month), int(day), hour, int(minute), int(second),
                              int(millisecond) * 1000) + timedelta(hours=hour_offset)
    except:
        return 'Invalid Timestamp'
    return _timestamp


f = open("E:\INTECH\Projects\PARCO MFM\ldsTesting\Fahad_code_test\Test2set2_short.txt", "r")
buffers = []
for x in f:
    a = json.loads(x)
    print(decode_time(708, a['NPW_array_PT_2084']))
    buffers.append(decode(708, a['NPW_array_PT_2084']))

xvals1 = [i for i in range(350)]
xvals2 = [i-2 for i in range(350)]
print(buffers)
plt.plot(xvals1, buffers[1])
plt.plot(xvals2, buffers[3])
plt.show()

