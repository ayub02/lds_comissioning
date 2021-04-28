

def decode(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    _pVal = []
    for i in range(8, _buffer_len, 2):
        _pVal.append((_buffer[i] << 8) + _buffer[i + 1])
    return _pVal

f = open("../data/fahad_results.txt", "r")
for i in range(1):
    print([qty/1000 for qty in decode(1008, [int(val) for val in (f.readline()).split(',')])])

