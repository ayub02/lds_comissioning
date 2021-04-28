import tkinter
from tkinter import *
from tkcalendar import *
import psycopg2
import datetime
from psycopg2 import sql
import pandas as pd
from itertools import cycle
from functools import partial
from datetime import datetime
from matplotlib import pyplot as plt


def get_data(_tag):
    if option_var.get() == 1:
        _query = sql.SQL("SELECT * FROM historytableaug20 where itemid= %s ORDER BY itemtimestamp DESC LIMIT %s;")
        cursor.execute(_query, (_tag, int(clicked5.get())))

    if option_var.get() == 2:
        from_month, from_day, from_year = cal_from.get_date().split('/')
        to_month, to_day, to_year = cal_to.get_date().split('/')

        _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), 0, 0, 0)
        _to_date = datetime(int('20' + to_year), int(to_month), int(to_day) + 1, 0, 0, 0)
        if _from_date >= _to_date:
            return None, None, None, None, None, 'Start date cannot be greater than end date'

        _query = sql.SQL("SELECT * FROM historytableaug20 WHERE itemid= %s AND itemtimestamp BETWEEN %s AND %s;")
        cursor.execute(_query, (_tag, _from_date, _to_date))

    _rows = cursor.fetchall()
    _opcTag = []
    _rawBuffer = []
    _opcTimestamp = []
    _pVal = []
    _bufferTimestamp = []
    if _rows:
        for _row in _rows:
            _buffer = [int(val) for val in _row[1].split(",")]
            _opcTag.append(_row[0])
            _rawBuffer.append(_buffer)
            _opcTimestamp.append(_row[2])
            _pVal.append(decode(1008, _buffer))
            _bufferTimestamp.append(decode_time(1008, _buffer))
        return _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, "Found " + str(len(_opcTag)) + " records"
    return None, None, None, None, None, "No records found"


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
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), int(millisecond) * 1000)


def decode(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    _pVal = []
    for i in range(8, _buffer_len, 2):
        _pVal.append((_buffer[i] << 8) + _buffer[i + 1])
    return _pVal


def format_time(_t):
    _s = _t.strftime('%Y-%m-%d %H:%M:%S.%f')
    return _s[:-3]


def refresh():
    update_listbox(1, clicked1.get())
    update_listbox(2, clicked2.get())
    update_listbox(3, clicked3.get())
    update_listbox(4, clicked4.get())


def update_listbox(_id, _selection):
    if _id == 1:
        _lbx = lbx1
    if _id == 2:
        _lbx = lbx2
    if _id == 3:
        _lbx = lbx3
    if _id == 4:
        _lbx = lbx4

    _lbx.delete(0, END)
    if _selection == 'Select':
        _lbx.insert(END, [])
        log.set('')
    else:
        _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, _message = get_data(tag_dict[_selection])
        log.set(_message)
        _dfData = []
        if _opcTag:
            for i in range(len(_opcTag)):
                _dfData.append([_opcTag[i], _rawBuffer[i], _opcTimestamp[i], _pVal[i], _bufferTimestamp[i]])
            _lbx.df = pd.DataFrame(_dfData, columns=['OPC_Tag', 'Buffer', 'OPC_timestamp', 'Pressure_values',
                                                     'Buffer_timestamp'])
            for val in _lbx.df['OPC_timestamp']:
                _lbx.insert(END, val.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


def newPlot(_overlay):
    _idx1 = lbx1.curselection()
    _idx2 = lbx2.curselection()
    _idx3 = lbx3.curselection()
    _idx4 = lbx4.curselection()
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
    else:
        log.set('No timestamp has been selected')
        return

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
            T.delete(1.0, END)
            if type(_lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]) is str:
                T.insert(END, "Buffer timestamp:    " +
                         _lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0] +
                         '\nBuffer:\n' + ",".join(
                    [str(val) for val in _lbx.df['Buffer'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]]))
            else:
                T.insert(END, "Buffer timestamp:    " +
                         _lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0].strftime(
                             '%Y-%m-%d %H:%M:%S.%f')[:-3] +
                         '\nBuffer:\n' + ",".join(
                    [str(val) for val in _lbx.df['Buffer'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0]]))


def next_plot():
    return next(line_cycle), next(color_cycle)


def func_plot(_OPC_Tag, _buffer, _OPC_timestamp, _pVal, _buffer_timestamp, _on_existing=False):
    if _on_existing is False:
        plt.figure()
        _linestyle = '-'
        _color = 'b'
    else:
        _linestyle, _color = next_plot()

    plt.xlabel('Number of values')
    plt.ylabel('Pressure (Pa)')
    if _buffer_timestamp == 'Invalid Timestamp':
        plt.plot(_pVal, linestyle=_linestyle, color=_color, label=_OPC_Tag + '     ' + _buffer_timestamp)
    else:
        plt.plot(_pVal, linestyle=_linestyle, color=_color, label=_OPC_Tag + '     ' + _buffer_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    plt.legend(bbox_to_anchor=(1, 1.16), fontsize='x-small')
    plt.show()


num_datasets = [5, 10, 20, 50, 100]
tags = ['Select', 'MKT', 'MOV60', 'BV61', 'BV62', 'BV63', 'BV64', 'BV65', 'BV66', 'MOV67', 'KBS']
tag_dict = {'MKT': 'MKT_out.NPW.ByteArray', 'MOV60': 'MOV60.NPW.ByteArray', 'BV61': 'BV61.NPW.ByteArray',
            'BV62': 'BV62.NPW.ByteArray', 'BV63': 'BV63.NPW.ByteArray', 'BV64': 'BV64.NPW.ByteArray',
            'BV65': 'BV65.NPW.ByteArray', 'BV66': 'BV66.NPW.ByteArray', 'MOV67': 'MOV67.NPW.ByteArray',
            'KBS': 'KBS_in.NPW.ByteArray'}

# Connecting to database
while True:
    try:
        print('Connecting to database')
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='@intech#123', host='10.1.17.113',
                                port='5432')
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}'.format(e))
    else:
        print('Connected!')
        break

conn.autocommit = True
cursor = conn.cursor()

line_cycle =  cycle(['--', ':', '-.', '-', '--', ':', '-.', '-'])
color_cycle = cycle(['k',  'b', 'r',  'y', 'y',  'k', 'b',  'r'])

root = tkinter.Tk()

# Drop down variable
clicked1 = StringVar()
clicked2 = StringVar()
clicked3 = StringVar()
clicked4 = StringVar()
clicked5 = StringVar()
log = StringVar()

clicked1.set(tags[0])
clicked2.set(tags[0])
clicked3.set(tags[0])
clicked4.set(tags[0])
clicked5.set(num_datasets[1])

# Radiobutton variable
option_var = IntVar()
option_var.set(1)

# Widget descriptions
fr1 = Frame(root)
fr2 = Frame(root)
fr3 = Frame(root)
fr4 = Frame(root)

lbx1 = Listbox(fr1, font=("Verdana", 8), height=16, width=30)
lbx2 = Listbox(fr2, font=("Verdana", 8), height=16, width=30)
lbx3 = Listbox(fr3, font=("Verdana", 8), height=16, width=30)
lbx4 = Listbox(fr4, font=("Verdana", 8), height=16, width=30)

sbr1 = Scrollbar(fr1, )
sbr2 = Scrollbar(fr2, )
sbr3 = Scrollbar(fr3, )
sbr4 = Scrollbar(fr4, )

drop1 = OptionMenu(root, clicked1, *tags, command=partial(update_listbox, 1))
drop2 = OptionMenu(root, clicked2, *tags, command=partial(update_listbox, 2))
drop3 = OptionMenu(root, clicked3, *tags, command=partial(update_listbox, 3))
drop4 = OptionMenu(root, clicked4, *tags, command=partial(update_listbox, 4))
drop5 = OptionMenu(root, clicked5, *num_datasets)

newPlotButton1 = Button(root, text="Plot New", command=partial(newPlot, False))
extPlotButton1 = Button(root, text="Plot Overlay", command=partial(newPlot, True))
refresh = Button(root, text="Refresh", command=refresh)

R1 = Radiobutton(root, text="Last", variable=option_var, value=1)
R2 = Radiobutton(root, text="Dates", variable=option_var, value=2)

label1 = Label(root, text="timestamps")
label2 = Label(root, text="From")
label3 = Label(root, text="To")
messageBox = Label(root, textvariable=log, height=1, width=100, anchor="w")

now = datetime.now()
cal_from = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)

T = Text(root, height=10, width=180)

# Widget positions
fr1.grid(row=1, column=0, rowspan=3, columnspan=2, sticky='nw')
fr2.grid(row=1, column=2, rowspan=3, columnspan=2, sticky='nw')
fr3.grid(row=1, column=4, rowspan=3, columnspan=2, sticky='nw')
fr4.grid(row=1, column=6, rowspan=3, columnspan=2, sticky='nw')

sbr1.pack(side=RIGHT, fill="y")
sbr2.pack(side=RIGHT, fill="y")
sbr3.pack(side=RIGHT, fill="y")
sbr4.pack(side=RIGHT, fill="y")

lbx1.pack()
lbx2.pack()
lbx3.pack()
lbx4.pack()

drop1.grid(row=0, column=0)
drop2.grid(row=0, column=2)
drop3.grid(row=0, column=4)
drop4.grid(row=0, column=6)
drop5.grid(row=0, column=10)

newPlotButton1.grid(row=0, column=12, sticky='w')
extPlotButton1.grid(row=0, column=13, sticky='w')
refresh.grid(row=0, column=14, sticky='w')

R1.grid(row=0, column=9, sticky='w')
R2.grid(row=1, column=9, sticky='w')

# label1.grid(row=0, column=11)
label2.grid(row=2, column=10)
label3.grid(row=2, column=13)

cal_from.grid(row=3, column=9, columnspan=3)
cal_to.grid(row=3, column=12, columnspan=3)

messageBox.grid(row=4, column=0, columnspan=8, sticky='w')
T.grid(row=5, columnspan=15, sticky='w')

# Connecting listbox and scroll
sbr1.config(command=lbx1.yview)
sbr2.config(command=lbx2.yview)
sbr3.config(command=lbx3.yview)
sbr4.config(command=lbx4.yview)

lbx1.config(yscrollcommand=sbr1.set)
lbx2.config(yscrollcommand=sbr2.set)
lbx3.config(yscrollcommand=sbr3.set)
lbx4.config(yscrollcommand=sbr4.set)

lbx1.bind('<<ListboxSelect>>', lbx_select)
lbx2.bind('<<ListboxSelect>>', lbx_select)
lbx3.bind('<<ListboxSelect>>', lbx_select)
lbx4.bind('<<ListboxSelect>>', lbx_select)

root.mainloop()
