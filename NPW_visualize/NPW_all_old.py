import os
import tkinter
import psycopg2
import datetime
import configparser
import pandas as pd
from tkinter import *
from tkcalendar import *
from psycopg2 import sql
from itertools import cycle
from functools import partial
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


def get_data(_tag):
    if option_var.get() == 1:
        _query = sql.SQL("SELECT * FROM {} where itemid= %s ORDER BY itemtimestamp DESC LIMIT %s;").format(sql.Identifier(table))
        print(datetime.now(), '\t', _tag, '\tFetching data .........')
        cursor.execute(_query, (_tag, int(clicked15.get())))

    if option_var.get() == 2:
        from_month, from_day, from_year = cal_from.get_date().split('/')
        to_month, to_day, to_year = cal_to.get_date().split('/')

        _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), 0, 0, 0)
        _to_date = datetime(int('20' + to_year), int(to_month), int(to_day), 23, 59, 59)
        if _from_date >= _to_date:
            return None, None, None, None, None, 'Start date cannot be greater than end date'

        _query = sql.SQL("SELECT * FROM {} WHERE itemid= %s AND itemtimestamp BETWEEN %s AND %s ORDER BY itemtimestamp DESC;").format(sql.Identifier(table))
        print(datetime.now(), '   Fetching data for ', _tag)
        cursor.execute(_query, (_tag, _from_date, _to_date))

    print(datetime.now(), '\t', _tag, '\tFetch completed')

    _rows = cursor.fetchall()
    _opcTag = []
    _rawBuffer = []
    _opcTimestamp = []
    _pVal = []
    _bufferTimestamp = []
    if _rows:
        print(datetime.now(), '\t', _tag, '\tProcessing data .........')
        for _row in _rows:
            _buffer = [int(val) for val in _row[1].split(",")]
            _opcTag.append(_row[0])
            _rawBuffer.append(_buffer)
            _opcTimestamp.append(_row[2])
            _pVal.append(decode(1008, _buffer))
            _bufferTimestamp.append(decode_time(1008, _buffer))
        print(datetime.now(), '\t', _tag, '\tProcessing completed')
        return _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, "Found " + str(len(_opcTag)) + " records"
    return None, None, None, None, None, "No records found"


def decode_time(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
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

    try:
        _timestamp = datetime(int(year), int(month), int(day), hour, int(minute), int(second), int(millisecond)* 1000) + timedelta(hours=hour_offset)
    except:
        return 'Invalid Timestamp'
    return _timestamp


def decode(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    _pVal = []
    for i in range(8, _buffer_len, 2):
        _pVal.append(((_buffer[i] << 8) + _buffer[i + 1])/500)
    return _pVal


def format_time(_t):
    _s = _t.strftime('%Y-%m-%d %H:%M:%S.%f')
    return _s[:-3]


def new_update_listbox(_lbx, _log, _tag):
    _lbx.delete(0, END)
    _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, _message = get_data(_tag)
    _log.set(_message)
    _dfData = []
    if _opcTag:
        for i in range(len(_opcTag)):
            _dfData.append([_opcTag[i], _rawBuffer[i], _opcTimestamp[i], _pVal[i], _bufferTimestamp[i]])
        _lbx.df = pd.DataFrame(_dfData, columns=['OPC_Tag', 'Buffer', 'OPC_timestamp', 'Pressure_values',
                                                 'Buffer_timestamp'])
        for val in _lbx.df['OPC_timestamp']:
            _lbx.insert(END, val.strftime('%Y-%m-%d %H:%M:%S'))                                         # Important


def update_listbox():
    new_update_listbox(lbx1, log1, 'NPW_array_PT_2003')
    new_update_listbox(lbx2, log2, 'NPW_array_PT_61')
    new_update_listbox(lbx3, log3, 'NPW_array_PT_62')
    new_update_listbox(lbx4, log4, 'NPW_array_PT_63')
    new_update_listbox(lbx5, log5, 'NPW_array_PT_64')
    new_update_listbox(lbx6, log6, 'NPW_array_PT_65')
    new_update_listbox(lbx7, log7, 'NPW_array_PT_66')
    new_update_listbox(lbx8, log8, 'NPW_array_PT_66A')
    new_update_listbox(lbx9, log9, 'NPW_array_PT_3025')
    new_update_listbox(lbx10, log10, 'NPW_array_PT_3026')
    new_update_listbox(lbx11, log11, 'NPW_array_PT_69')
    new_update_listbox(lbx12, log12, 'NPW_array_PT_70')
    new_update_listbox(lbx13, log13, 'NPW_array_PT_70A')
    new_update_listbox(lbx14, log14, 'NPW_array_PT_71')
    new_update_listbox(lbx15, log15, 'NPW_array_PT_72')
    new_update_listbox(lbx16, log16, 'NPW_array_PT_72A')
    new_update_listbox(lbx17, log17, 'NPW_array_PT_4025')
    new_update_listbox(lbx18, log18, 'NPW_array_PT_4026')
    new_update_listbox(lbx19, log19, 'NPW_array_PT_74A')
    new_update_listbox(lbx20, log20, 'NPW_array_PT_75')
    new_update_listbox(lbx21, log21, 'NPW_array_PT_76')
    new_update_listbox(lbx22, log22, 'NPW_array_PT_5000A')


def export_func():
    newPlot(False, True)


def newPlot(_overlay, _export=False):
    _idx1 = lbx1.curselection()
    _idx2 = lbx2.curselection()
    _idx3 = lbx3.curselection()
    _idx4 = lbx4.curselection()
    _idx5 = lbx5.curselection()
    _idx6 = lbx6.curselection()
    _idx7 = lbx7.curselection()
    _idx8 = lbx8.curselection()
    _idx9 = lbx9.curselection()
    _idx10 = lbx10.curselection()
    _idx11 = lbx11.curselection()
    _idx12 = lbx12.curselection()
    _idx13 = lbx13.curselection()
    _idx14 = lbx14.curselection()
    _idx15 = lbx15.curselection()
    _idx16 = lbx16.curselection()
    _idx17 = lbx17.curselection()
    _idx18 = lbx18.curselection()
    _idx19 = lbx19.curselection()
    _idx20 = lbx20.curselection()
    _idx21 = lbx21.curselection()
    _idx22 = lbx22.curselection()
    if _idx1:
        _idx = _idx1
        _lbx = lbx1
    elif _idx2:
        _idx = _idx2
        _lbx = lbx2
    elif _idx3:
        _idx = _idx3
        _lbx = lbx3
    elif _idx4:
        _idx = _idx4
        _lbx = lbx4
    elif _idx5:
        _idx = _idx5
        _lbx = lbx5
    elif _idx6:
        _idx = _idx6
        _lbx = lbx6
    elif _idx7:
        _idx = _idx7
        _lbx = lbx7
    elif _idx8:
        _idx = _idx8
        _lbx = lbx8
    elif _idx9:
        _idx = _idx9
        _lbx = lbx9
    if _idx10:
        _idx = _idx10
        _lbx = lbx10
    elif _idx11:
        _idx = _idx11
        _lbx = lbx11
    elif _idx12:
        _idx = _idx12
        _lbx = lbx12
    elif _idx13:
        _idx = _idx13
        _lbx = lbx13
    elif _idx14:
        _idx = _idx14
        _lbx = lbx14
    elif _idx15:
        _idx = _idx15
        _lbx = lbx15
    elif _idx16:
        _idx = _idx16
        _lbx = lbx16
    elif _idx17:
        _idx = _idx17
        _lbx = lbx17
    elif _idx18:
        _idx = _idx18
        _lbx = lbx18
    elif _idx19:
        _idx = _idx19
        _lbx = lbx19
    elif _idx20:
        _idx = _idx20
        _lbx = lbx20
    elif _idx21:
        _idx = _idx21
        _lbx = lbx21
    elif _idx22:
        _idx = _idx22
        _lbx = lbx22
    else:
        log.set('No timestamp has been selected')
        return
    log.set(' ')
    if _export:
        _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%Y-%m-%d %H:%M:%S.%f'))
        _tag = _lbx.df['OPC_Tag'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]
        _rawBuffer = _lbx.df['Buffer'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]
        _opcTimestamp = _lbx.df['OPC_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]
        _pVal = _lbx.df['Pressure_values'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]
        _bufferTimestamp = _lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]

        _dict = {'OPC Tag': _tag, 'OPC Timestamp:': _opcTimestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                 'Buffer Timestamp': _bufferTimestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                 'Raw buffer': [_rawBuffer], 'Pressure Values': [_pVal]}

        _df = pd.DataFrame(data=_dict)
        _filename = (_tag + '__' + 'opc' + '__' + _opcTimestamp.strftime('%Y_%m_%d__%H_%M_%S') + '__' + 'edge' + '__' +
                     _bufferTimestamp.strftime('%Y_%m_%d__%H_%M_%S')).replace('.', '_')
        _filename = _filename + '.csv'
        _path = '../output/'
        if os.path.exists(_path+_filename):
            os.remove(_path+_filename)
            print('Removed ', _filename)
        else:
            _df.to_csv(_path+_filename, index=False)
            print('File write successful \t\t', _filename)

    else:
        _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%Y-%m-%d %H:%M:%S'))
        func_plot(_lbx.df['OPC_Tag'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Buffer'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['OPC_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Pressure_values'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _on_existing=_overlay)


# def lbx_select(_event):
#     _lbx = _event.widget
#     _idx = _lbx.curselection()
#     if _idx:
#         if _lbx.get(_idx):
#             _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%Y-%m-%d %H:%M:%S.%f'))


def next_plot():
    return next(line_cycle), next(color_cycle)


def func_plot(_OPC_Tag, _buffer, _OPC_timestamp, _pVal, _buffer_timestamp, _on_existing=False):
    if pressure_var.get() == 1:
        _pVal_offset = [val - _pVal[0] for val in _pVal]
        _pVal_to_plot = _pVal_offset
    else:
        _pVal_to_plot = _pVal
    sample_nums = [_val for _val in range(500)]
    _pmax = max(_pVal_to_plot)
    _pmin = min(_pVal_to_plot)
    _dP = _pmin - _pmax

    for i, _val in enumerate(_pVal_to_plot):
        if _val <= _pmin+abs(_dP*0.8):
            _p80 = _val
            _i80 = i
            break

    for i, _val in enumerate(_pVal_to_plot):
        if _val <= _pmin + abs(_dP*0.3):
            _p30 = _val
            _i30 = i
            break

    if _i80-_i30 == 0:
        _gradient = 99999
    else:
        _gradient = (_p80-_p30)/(_i80-_i30)/0.1

    if _on_existing is False:
        plt.figure()
        _linestyle = '-'
        _color = 'b'
    else:
        _linestyle, _color = next_plot()

    plt.xlabel('Number of values')
    plt.ylabel('Pressure (bar)')
    if _buffer_timestamp == 'Invalid Timestamp':
        plt.plot(_pVal_to_plot, linestyle=_linestyle, color=_color, label='dP: ' + str(round(_dP, 3)) + ' bar   ' + 'grad: ' + str(round(_gradient, 3)) + '   '
                                                                          + _OPC_Tag + '     ' + 'OPC TS:'
                                                                          + _OPC_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                                                          + '    Buffer TS:' + _buffer_timestamp)
        plt.plot([_i80, _i30], [_p80, _p30], color='yellow', linestyle='--')
    else:
        plt.plot(_pVal_to_plot, linestyle=_linestyle, color=_color, label='dP: ' + str(round(_dP, 3)) + ' bar   ' + 'grad: ' + str(round(_gradient, 3)) + '   '
                                                                          + _OPC_Tag + '     ' + 'OPC TS:'
                                                                          + _OPC_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                                                          + '    Buffer TS:' + _buffer_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        plt.plot([_i80, _i30], [_p80, _p30], color='yellow', linestyle='--')
    plt.legend(fontsize='x-small') #bbox_to_anchor=(1, 1.16),
    plt.show()


# *********************************************************************************************************************
# *********************************************************************************************************************
# *********************************************************************************************************************
config = configparser.ConfigParser()
config.read('../config/database.ini')

host = config['postgresql']['host']
database = config['postgresql']['database']
user = config['postgresql']['user']
password = config['postgresql']['password']
table = config['postgresql']['table']
port = config['postgresql']['port']

num_datasets = [10, 50, 200, 500]

line_cycle = cycle(['--', ':', '-.', ':', '--', ':', '-.', ':'])
color_cycle = cycle(['k',  'b', 'r',  'y', 'y',  'k', 'b',  'r'])

# *********************************************************************************************************************
# *********************************************************************************************************************
# *********************************************************************************************************************

# Connecting to database
while True:
    try:
        print('Connecting to database')
        conn = psycopg2.connect(dbname=database, user=user, password=password, host=host, port=port)
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}'.format(e))
    else:
        print('Connected!')
        break

conn.autocommit = True
cursor = conn.cursor()

font_size = 7
lbox_width = 18
mBoxColor = 'pale green'
root = tkinter.Tk()

# Drop down variable
clicked15 = StringVar()

log = StringVar()
log1 = StringVar()
log2 = StringVar()
log3 = StringVar()
log4 = StringVar()
log5 = StringVar()
log6 = StringVar()
log7 = StringVar()
log8 = StringVar()
log9 = StringVar()
log10 = StringVar()
log11 = StringVar()
log12 = StringVar()
log13 = StringVar()
log14 = StringVar()
log15 = StringVar()
log16 = StringVar()
log17 = StringVar()
log18 = StringVar()
log19 = StringVar()
log20 = StringVar()
log21 = StringVar()
log22 = StringVar()


clicked15.set(num_datasets[3])

# Radiobutton variable
option_var = IntVar()
pressure_var = IntVar()
direction_var = IntVar()
option_var.set(1)
pressure_var.set(1)
direction_var.set(1)

# Widget descriptions
fr1 = Frame(root)
fr2 = Frame(root)
fr3 = Frame(root)
fr4 = Frame(root)
fr5 = Frame(root)
fr6 = Frame(root)
fr7 = Frame(root)
fr8 = Frame(root)
fr9 = Frame(root)
fr10 = Frame(root)
fr11 = Frame(root)
fr12 = Frame(root)
fr13 = Frame(root)
fr14 = Frame(root)
fr15 = Frame(root)
fr16 = Frame(root)
fr17 = Frame(root)
fr18 = Frame(root)
fr19 = Frame(root)
fr20 = Frame(root)
fr21 = Frame(root)
fr22 = Frame(root)

lbx1 = Listbox(fr1, font=("Verdana", font_size), height=16, width=lbox_width)
lbx2 = Listbox(fr2, font=("Verdana", font_size), height=16, width=lbox_width)
lbx3 = Listbox(fr3, font=("Verdana", font_size), height=16, width=lbox_width)
lbx4 = Listbox(fr4, font=("Verdana", font_size), height=16, width=lbox_width)
lbx5 = Listbox(fr5, font=("Verdana", font_size), height=16, width=lbox_width)
lbx6 = Listbox(fr6, font=("Verdana", font_size), height=16, width=lbox_width)
lbx7 = Listbox(fr7, font=("Verdana", font_size), height=16, width=lbox_width)
lbx8 = Listbox(fr8, font=("Verdana", font_size), height=16, width=lbox_width)
lbx9 = Listbox(fr9, font=("Verdana", font_size), height=16, width=lbox_width)
lbx10 = Listbox(fr10, font=("Verdana", font_size), height=16, width=lbox_width)
lbx11 = Listbox(fr11, font=("Verdana", font_size), height=16, width=lbox_width)
lbx12 = Listbox(fr12, font=("Verdana", font_size), height=16, width=lbox_width)
lbx13 = Listbox(fr13, font=("Verdana", font_size), height=16, width=lbox_width)
lbx14 = Listbox(fr14, font=("Verdana", font_size), height=16, width=lbox_width)
lbx15 = Listbox(fr15, font=("Verdana", font_size), height=16, width=lbox_width)
lbx16 = Listbox(fr16, font=("Verdana", font_size), height=16, width=lbox_width)
lbx17 = Listbox(fr17, font=("Verdana", font_size), height=16, width=lbox_width)
lbx18 = Listbox(fr18, font=("Verdana", font_size), height=16, width=lbox_width)
lbx19 = Listbox(fr19, font=("Verdana", font_size), height=16, width=lbox_width)
lbx20 = Listbox(fr20, font=("Verdana", font_size), height=16, width=lbox_width)
lbx21 = Listbox(fr21, font=("Verdana", font_size), height=16, width=lbox_width)
lbx22 = Listbox(fr22, font=("Verdana", font_size), height=16, width=lbox_width)

frame_xpad = 3
fr1.grid(row=1, column=0, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr2.grid(row=1, column=1, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr3.grid(row=1, column=2, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr4.grid(row=1, column=3, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr5.grid(row=1, column=4, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr6.grid(row=1, column=5, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr7.grid(row=1, column=6, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr8.grid(row=1, column=7, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr9.grid(row=1, column=8, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr10.grid(row=1, column=9, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr11.grid(row=6, column=0, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr12.grid(row=6, column=1, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr13.grid(row=6, column=2, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr14.grid(row=6, column=3, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr15.grid(row=6, column=4, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr16.grid(row=6, column=5, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr17.grid(row=6, column=6, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr18.grid(row=6, column=7, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr19.grid(row=6, column=8, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr20.grid(row=6, column=9, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr21.grid(row=11, column=8, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')
fr22.grid(row=11, column=9, rowspan=3, columnspan=1, padx=frame_xpad, sticky='nw')

sbr1 = Scrollbar(fr1, )
sbr2 = Scrollbar(fr2, )
sbr3 = Scrollbar(fr3, )
sbr4 = Scrollbar(fr4, )
sbr5 = Scrollbar(fr5, )
sbr6 = Scrollbar(fr6, )
sbr7 = Scrollbar(fr7, )
sbr8 = Scrollbar(fr8, )
sbr9 = Scrollbar(fr9, )
sbr10 = Scrollbar(fr10, )
sbr11 = Scrollbar(fr11, )
sbr12 = Scrollbar(fr12, )
sbr13 = Scrollbar(fr13, )
sbr14 = Scrollbar(fr14, )
sbr15 = Scrollbar(fr15, )
sbr16 = Scrollbar(fr16, )
sbr17 = Scrollbar(fr17, )
sbr18 = Scrollbar(fr18, )
sbr19 = Scrollbar(fr19, )
sbr20 = Scrollbar(fr20, )
sbr21 = Scrollbar(fr21, )
sbr22 = Scrollbar(fr22, )

sbr1.pack(side=RIGHT, fill="y")
sbr2.pack(side=RIGHT, fill="y")
sbr3.pack(side=RIGHT, fill="y")
sbr4.pack(side=RIGHT, fill="y")
sbr5.pack(side=RIGHT, fill="y")
sbr6.pack(side=RIGHT, fill="y")
sbr7.pack(side=RIGHT, fill="y")
sbr8.pack(side=RIGHT, fill="y")
sbr9.pack(side=RIGHT, fill="y")
sbr10.pack(side=RIGHT, fill="y")
sbr11.pack(side=RIGHT, fill="y")
sbr12.pack(side=RIGHT, fill="y")
sbr13.pack(side=RIGHT, fill="y")
sbr14.pack(side=RIGHT, fill="y")
sbr15.pack(side=RIGHT, fill="y")
sbr16.pack(side=RIGHT, fill="y")
sbr17.pack(side=RIGHT, fill="y")
sbr18.pack(side=RIGHT, fill="y")
sbr19.pack(side=RIGHT, fill="y")
sbr20.pack(side=RIGHT, fill="y")
sbr21.pack(side=RIGHT, fill="y")
sbr22.pack(side=RIGHT, fill="y")

lbx1.pack()
lbx2.pack()
lbx3.pack()
lbx4.pack()
lbx5.pack()
lbx6.pack()
lbx7.pack()
lbx8.pack()
lbx9.pack()
lbx10.pack()
lbx11.pack()
lbx12.pack()
lbx13.pack()
lbx14.pack()
lbx15.pack()
lbx16.pack()
lbx17.pack()
lbx18.pack()
lbx19.pack()
lbx20.pack()
lbx21.pack()
lbx22.pack()

drop15 = OptionMenu(root, clicked15, *num_datasets).grid(row=10, column=1, sticky='w')

newPlotButton1 = Button(root, text="Plot New", command=partial(newPlot, False)).grid(row=10, column=2, sticky='w')
extPlotButton1 = Button(root, text="Plot Overlay", command=partial(newPlot, True)).grid(row=10, column=3, sticky='w')
exportExcel = Button(root, text="Export csv", command=export_func).grid(row=10, column=4, sticky='w')
refresh = Button(root, text="Refresh", command=update_listbox).grid(row=10, column=5, sticky='w')

R1 = Radiobutton(root, text="Last", variable=option_var, value=1).grid(row=10, column=0, sticky='w')
R2 = Radiobutton(root, text="Dates", variable=option_var, value=2).grid(row=11, column=0, sticky='w')

radio_ref = Radiobutton(root, text="Zero reference pressure", variable=pressure_var, value=1).grid(row=10, column=6, sticky='w')
radio_orig = Radiobutton(root, text="Original pressure", variable=pressure_var, value=2).grid(row=11, column=6, sticky='w')


label2 = Label(root, text="From").grid(row=11, column=2)
label3 = Label(root, text="To").grid(row=11, column=3)

label_1 = Label(root, text="MKT", justify=CENTER).grid(row=0, column=0)
label_2 = Label(root, text="BV61", justify=CENTER).grid(row=0, column=1)
label_3 = Label(root, text="BV62", justify=CENTER).grid(row=0, column=2)
label_4 = Label(root, text="BV63", justify=CENTER).grid(row=0, column=3)
label_5 = Label(root, text="BV64", justify=CENTER).grid(row=0, column=4)
label_6 = Label(root, text="BV65", justify=CENTER).grid(row=0, column=5)
label_7 = Label(root, text="BV66", justify=CENTER).grid(row=0, column=6)
label_8 = Label(root, text="BV66A", justify=CENTER).grid(row=0, column=7)
label_9 = Label(root, text="KBS_3025", justify=CENTER).grid(row=0, column=8)
label_10 = Label(root, text="KBS_3026", justify=CENTER).grid(row=0, column=9)
label_11 = Label(root, text="BV69", justify=CENTER).grid(row=5, column=0)
label_12 = Label(root, text="BV70", justify=CENTER).grid(row=5, column=1)
label_13 = Label(root, text="BV70A", justify=CENTER).grid(row=5, column=2)
label_14 = Label(root, text="BV71", justify=CENTER).grid(row=5, column=3)
label_15 = Label(root, text="BV72", justify=CENTER).grid(row=5, column=4)
label_16 = Label(root, text="BV72A", justify=CENTER).grid(row=5, column=5)
label_17 = Label(root, text="FSD_4025", justify=CENTER).grid(row=5, column=6)
label_18 = Label(root, text="FSD_4026", justify=CENTER).grid(row=5, column=7)
label_19 = Label(root, text="BV74A", justify=CENTER).grid(row=5, column=8)
label_20 = Label(root, text="BV75", justify=CENTER).grid(row=5, column=9)
label_21 = Label(root, text="BV76", justify=CENTER).grid(row=10, column=8)
label_22 = Label(root, text="MCK_5000A", justify=CENTER).grid(row=10, column=9)

mBox1 = Label(root, textvariable=log1, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=0, sticky='w')
mBox2 = Label(root, textvariable=log2, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=1, sticky='w')
mBox3 = Label(root, textvariable=log3, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=2, sticky='w')
mBox4 = Label(root, textvariable=log4, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=3, sticky='w')
mBox5 = Label(root, textvariable=log5, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=4, sticky='w')
mBox6 = Label(root, textvariable=log6, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=5, sticky='w')
mBox7 = Label(root, textvariable=log7, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=6, sticky='w')
mBox8 = Label(root, textvariable=log8, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=7, sticky='w')
mBox9 = Label(root, textvariable=log9, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=8, sticky='w')
mBox10 = Label(root, textvariable=log10, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=4, column=9, sticky='w')
mBox11 = Label(root, textvariable=log11, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=0, sticky='w')
mBox12 = Label(root, textvariable=log12, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=1, sticky='w')
mBox13 = Label(root, textvariable=log13, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=2, sticky='w')
mBox14 = Label(root, textvariable=log14, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=3, sticky='w')
mBox15 = Label(root, textvariable=log15, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=4, sticky='w')
mBox16 = Label(root, textvariable=log16, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=5, sticky='w')
mBox17 = Label(root, textvariable=log17, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=6, sticky='w')
mBox18 = Label(root, textvariable=log18, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=7, sticky='w')
mBox19 = Label(root, textvariable=log19, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=8, sticky='w')
mBox20 = Label(root, textvariable=log20, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=9, column=9, sticky='w')
mBox21 = Label(root, textvariable=log21, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=14, column=8, sticky='w')
mBox22 = Label(root, textvariable=log22, height=1, width=lbox_width, anchor="w", bg=mBoxColor).grid(row=14, column=9, sticky='w')

now = datetime.now()

cal_from = Calendar(root, selectmode="day", year=(now-timedelta(days=1)).year, month=(now-timedelta(days=1)).month,
                    day=(now-timedelta(days=1)).day)
cal_from.grid(row=12, column=0, columnspan=2)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)
cal_to.grid(row=12, column=3, columnspan=3)

sbr1.config(command=lbx1.yview)
sbr2.config(command=lbx2.yview)
sbr3.config(command=lbx3.yview)
sbr4.config(command=lbx4.yview)
sbr5.config(command=lbx5.yview)
sbr6.config(command=lbx6.yview)
sbr7.config(command=lbx7.yview)
sbr8.config(command=lbx8.yview)
sbr9.config(command=lbx9.yview)
sbr10.config(command=lbx10.yview)
sbr11.config(command=lbx11.yview)
sbr12.config(command=lbx12.yview)
sbr13.config(command=lbx13.yview)
sbr14.config(command=lbx14.yview)
sbr15.config(command=lbx15.yview)
sbr16.config(command=lbx16.yview)
sbr17.config(command=lbx17.yview)
sbr18.config(command=lbx18.yview)
sbr19.config(command=lbx19.yview)
sbr20.config(command=lbx20.yview)
sbr21.config(command=lbx21.yview)
sbr22.config(command=lbx22.yview)

lbx1.config(yscrollcommand=sbr1.set)
lbx2.config(yscrollcommand=sbr2.set)
lbx3.config(yscrollcommand=sbr3.set)
lbx4.config(yscrollcommand=sbr4.set)
lbx5.config(yscrollcommand=sbr5.set)
lbx6.config(yscrollcommand=sbr6.set)
lbx7.config(yscrollcommand=sbr7.set)
lbx8.config(yscrollcommand=sbr8.set)
lbx9.config(yscrollcommand=sbr9.set)
lbx10.config(yscrollcommand=sbr10.set)
lbx11.config(yscrollcommand=sbr11.set)
lbx12.config(yscrollcommand=sbr12.set)
lbx13.config(yscrollcommand=sbr13.set)
lbx14.config(yscrollcommand=sbr14.set)
lbx15.config(yscrollcommand=sbr15.set)
lbx16.config(yscrollcommand=sbr16.set)
lbx17.config(yscrollcommand=sbr17.set)
lbx18.config(yscrollcommand=sbr18.set)
lbx19.config(yscrollcommand=sbr19.set)
lbx20.config(yscrollcommand=sbr20.set)
lbx21.config(yscrollcommand=sbr21.set)
lbx22.config(yscrollcommand=sbr22.set)

root.mainloop()
