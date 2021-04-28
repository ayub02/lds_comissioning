from datetime import datetime


def decode_time(_buffer_len, _buffer):
    hour_offset = 5                             # Hour offset implemented!!!
    if _buffer[0] >= 90:
        year = '19' + hex(_buffer[0])[2:]
    else:
        year = '20' + hex(_buffer[0])[2:]

    month = hex(_buffer[1])[2:]
    day = hex(_buffer[2])[2:]
    hour = int(hex(_buffer[3])[2:])
    minute = hex(_buffer[4])[2:]
    second = hex(_buffer[5])[2:]
    millisecond = hex(_buffer[6])[2:] + hex(int(_buffer[7]/16))[2]

    _timestamp = datetime(int(year), int(month), int(day), hour, int(minute), int(second), int(millisecond) * 1000)
    return _timestamp


# buffer = [32, 18, 3, 8, 9, 82, 120, 5]
buffer = [32, 18, 3, 5, 51, 51, 2, 101]
print(decode_time(1008, buffer))

