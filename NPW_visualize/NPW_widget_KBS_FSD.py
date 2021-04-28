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
            _lbx.insert(END, val.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


def update_listbox():
    new_update_listbox(lbx1, log1, 'NPW_array_PT_3026')
    new_update_listbox(lbx2, log2, 'NPW_array_PT_69')
    new_update_listbox(lbx3, log3, 'NPW_array_PT_70')
    new_update_listbox(lbx4, log4, 'NPW_array_PT_70A')
    new_update_listbox(lbx5, log5, 'NPW_array_PT_71')
    new_update_listbox(lbx6, log6, 'NPW_array_PT_72')
    new_update_listbox(lbx7, log7, 'NPW_array_PT_72A')
    new_update_listbox(lbx8, log8, 'NPW_array_PT_4025')
    new_update_listbox(lbx9, log9, 'NPW_array_PT_4026')


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
        _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%Y-%m-%d %H:%M:%S.%f'))
        func_plot(_lbx.df['OPC_Tag'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Buffer'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['OPC_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Pressure_values'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _on_existing=_overlay)


def lbx_select(_event):
    _lbx = _event.widget
    _idx = _lbx.curselection()
    if _idx:
        if _lbx.get(_idx):
            _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%Y-%m-%d %H:%M:%S.%f'))


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

time1 = StringVar()
time2 = StringVar()
time3 = StringVar()
time4 = StringVar()
time5 = StringVar()
time6 = StringVar()
time7 = StringVar()
time8 = StringVar()
time9 = StringVar()

time1.set('None')

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

lbx1 = Listbox(fr1, font=("Verdana", 8), height=16, width=21)
lbx2 = Listbox(fr2, font=("Verdana", 8), height=16, width=21)
lbx3 = Listbox(fr3, font=("Verdana", 8), height=16, width=21)
lbx4 = Listbox(fr4, font=("Verdana", 8), height=16, width=21)
lbx5 = Listbox(fr5, font=("Verdana", 8), height=16, width=21)
lbx6 = Listbox(fr6, font=("Verdana", 8), height=16, width=21)
lbx7 = Listbox(fr7, font=("Verdana", 8), height=16, width=21)
lbx8 = Listbox(fr8, font=("Verdana", 8), height=16, width=21)
lbx9 = Listbox(fr9, font=("Verdana", 8), height=16, width=21)

fr1.grid(row=1, column=0, rowspan=3, columnspan=1, sticky='nw')
fr2.grid(row=1, column=1, rowspan=3, columnspan=1, sticky='nw')
fr3.grid(row=1, column=2, rowspan=3, columnspan=1, sticky='nw')
fr4.grid(row=1, column=3, rowspan=3, columnspan=1, sticky='nw')
fr5.grid(row=1, column=4, rowspan=3, columnspan=1, sticky='nw')
fr6.grid(row=1, column=5, rowspan=3, columnspan=1, sticky='nw')
fr7.grid(row=1, column=6, rowspan=3, columnspan=1, sticky='nw')
fr8.grid(row=1, column=7, rowspan=3, columnspan=1, sticky='nw')
fr9.grid(row=1, column=8, rowspan=3, columnspan=1, sticky='nw')

sbr1 = Scrollbar(fr1, )
sbr2 = Scrollbar(fr2, )
sbr3 = Scrollbar(fr3, )
sbr4 = Scrollbar(fr4, )
sbr5 = Scrollbar(fr5, )
sbr6 = Scrollbar(fr6, )
sbr7 = Scrollbar(fr7, )
sbr8 = Scrollbar(fr8, )
sbr9 = Scrollbar(fr9, )

sbr1.pack(side=RIGHT, fill="y")
sbr2.pack(side=RIGHT, fill="y")
sbr3.pack(side=RIGHT, fill="y")
sbr4.pack(side=RIGHT, fill="y")
sbr5.pack(side=RIGHT, fill="y")
sbr6.pack(side=RIGHT, fill="y")
sbr7.pack(side=RIGHT, fill="y")
sbr8.pack(side=RIGHT, fill="y")
sbr9.pack(side=RIGHT, fill="y")

lbx1.pack()
lbx2.pack()
lbx3.pack()
lbx4.pack()
lbx5.pack()
lbx6.pack()
lbx7.pack()
lbx8.pack()
lbx9.pack()

drop15 = OptionMenu(root, clicked15, *num_datasets).grid(row=6, column=1, sticky='w')

newPlotButton1 = Button(root, text="Plot New", command=partial(newPlot, False)).grid(row=6, column=2, sticky='w')
extPlotButton1 = Button(root, text="Plot Overlay", command=partial(newPlot, True)).grid(row=6, column=3, sticky='w')
exportExcel = Button(root, text="Export csv", command=export_func).grid(row=6, column=4, sticky='w')
refresh = Button(root, text="Refresh", command=update_listbox).grid(row=6, column=5, sticky='w')


R1 = Radiobutton(root, text="Last", variable=option_var, value=1).grid(row=6, column=0, sticky='w')
R2 = Radiobutton(root, text="Dates", variable=option_var, value=2).grid(row=7, column=0, sticky='w')

radio_ref = Radiobutton(root, text="Zero reference pressure", variable=pressure_var, value=1).grid(row=6, column=7, sticky='w')
radio_orig = Radiobutton(root, text="Original pressure", variable=pressure_var, value=2).grid(row=7, column=7, sticky='w')

label1 = Label(root, text="timestamps")
label2 = Label(root, text="From").grid(row=7, column=2)
label3 = Label(root, text="To").grid(row=7, column=3)
label_log = Label(root, textvariable=log, height=1, width=217, anchor="w", bg='salmon1').grid(row=9, column=0,
                                                                                           columnspan=20, sticky='w')
label_1 = Label(root, text="KBS_3026", justify=CENTER).grid(row=0, column=0)
label_2 = Label(root, text="BV69", justify=CENTER).grid(row=0, column=1)
label_3 = Label(root, text="BV70", justify=CENTER).grid(row=0, column=2)
label_4 = Label(root, text="BV70A", justify=CENTER).grid(row=0, column=3)
label_5 = Label(root, text="BV71", justify=CENTER).grid(row=0, column=4)
label_6 = Label(root, text="BV72", justify=CENTER).grid(row=0, column=5)
label_7 = Label(root, text="BV72A", justify=CENTER).grid(row=0, column=6)
label_8 = Label(root, text="FSD1", justify=CENTER).grid(row=0, column=7)
label_9 = Label(root, text="FSD2", justify=CENTER).grid(row=0, column=8)

mBoxColor = 'pale green'
mBox1 = Label(root, textvariable=log1, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=0, sticky='w')
mBox2 = Label(root, textvariable=log2, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=1, sticky='w')
mBox3 = Label(root, textvariable=log3, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=2, sticky='w')
mBox4 = Label(root, textvariable=log4, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=3, sticky='w')
mBox5 = Label(root, textvariable=log5, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=4, sticky='w')
mBox6 = Label(root, textvariable=log6, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=5, sticky='w')
mBox7 = Label(root, textvariable=log7, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=6, sticky='w')
mBox8 = Label(root, textvariable=log8, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=7, sticky='w')
mBox9 = Label(root, textvariable=log9, height=1, width=22, anchor="w", bg=mBoxColor).grid(row=4, column=8, sticky='w')

timeLabelColor = 'LightSkyBlue1'
timeBox1 = Label(root, textvariable=time1, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=0, sticky='w')
timeBox2 = Label(root, textvariable=time2, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=1, sticky='w')
timeBox3 = Label(root, textvariable=time3, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=2, sticky='w')
timeBox4 = Label(root, textvariable=time4, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=3, sticky='w')
timeBox5 = Label(root, textvariable=time5, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=4, sticky='w')
timeBox6 = Label(root, textvariable=time6, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=5, sticky='w')
timeBox7 = Label(root, textvariable=time7, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=6, sticky='w')
timeBox8 = Label(root, textvariable=time8, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=7, sticky='w')
timeBox9 = Label(root, textvariable=time9, height=1, width=22, anchor="w", bg=timeLabelColor).grid(row=5, column=8, sticky='w')

now = datetime.now()

cal_from = Calendar(root, selectmode="day", year=(now-timedelta(days=1)).year, month=(now-timedelta(days=1)).month,
                    day=(now-timedelta(days=1)).day)
cal_from.grid(row=8, column=0, columnspan=2)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)
cal_to.grid(row=8, column=3, columnspan=3)

# **********************************************************************************************************************
# **********************************************************************************************************************
# Connecting listbox and scroll
# **********************************************************************************************************************
# **********************************************************************************************************************
sbr1.config(command=lbx1.yview)
sbr2.config(command=lbx2.yview)
sbr3.config(command=lbx3.yview)
sbr4.config(command=lbx4.yview)
sbr5.config(command=lbx5.yview)
sbr6.config(command=lbx6.yview)
sbr7.config(command=lbx7.yview)
sbr8.config(command=lbx8.yview)
sbr9.config(command=lbx9.yview)

lbx1.config(yscrollcommand=sbr1.set)
lbx2.config(yscrollcommand=sbr2.set)
lbx3.config(yscrollcommand=sbr3.set)
lbx4.config(yscrollcommand=sbr4.set)
lbx5.config(yscrollcommand=sbr5.set)
lbx6.config(yscrollcommand=sbr6.set)
lbx7.config(yscrollcommand=sbr7.set)
lbx8.config(yscrollcommand=sbr8.set)
lbx9.config(yscrollcommand=sbr9.set)

lbx1.bind('<<ListboxSelect>>', lbx_select)
lbx2.bind('<<ListboxSelect>>', lbx_select)
lbx3.bind('<<ListboxSelect>>', lbx_select)
lbx4.bind('<<ListboxSelect>>', lbx_select)
lbx5.bind('<<ListboxSelect>>', lbx_select)
lbx6.bind('<<ListboxSelect>>', lbx_select)
lbx7.bind('<<ListboxSelect>>', lbx_select)
lbx8.bind('<<ListboxSelect>>', lbx_select)
lbx9.bind('<<ListboxSelect>>', lbx_select)

root.mainloop()
