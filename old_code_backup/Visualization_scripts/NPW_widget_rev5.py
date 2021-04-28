import tkinter
from tkinter import *
from tkcalendar import *
import psycopg2
import datetime
import pandas as pd
from psycopg2 import sql
from itertools import cycle
from functools import partial
from datetime import datetime, timedelta
from matplotlib import pyplot as plt


def get_data(_tag):
    if option_var.get() == 1:
        _query = sql.SQL("SELECT * FROM mfmdata where itemid= %s ORDER BY itemtimestamp DESC LIMIT %s;")
        cursor.execute(_query, (_tag, int(clicked15.get())))

    if option_var.get() == 2:
        from_month, from_day, from_year = cal_from.get_date().split('/')
        to_month, to_day, to_year = cal_to.get_date().split('/')

        _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), 0, 0, 0)
        _to_date = datetime(int('20' + to_year), int(to_month), int(to_day) + 1, 0, 0, 0)
        if _from_date >= _to_date:
            return None, None, None, None, None, 'Start date cannot be greater than end date'

        _query = sql.SQL("SELECT * FROM mfmdata WHERE itemid= %s AND itemtimestamp BETWEEN %s AND %s ORDER BY itemtimestamp DESC;")
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
    millisecond = hex(_buffer[6])[2:] + hex(_buffer[7])[2]
    # datetime(year, month, day, hour, minute, second, microsecond)

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


def refresh():
    update_listbox(1, clicked1.get())
    update_listbox(2, clicked2.get())
    update_listbox(3, clicked3.get())
    update_listbox(4, clicked4.get())
    update_listbox(5, clicked5.get())
    update_listbox(6, clicked6.get())
    update_listbox(7, clicked7.get())
    update_listbox(8, clicked8.get())
    update_listbox(9, clicked9.get())


def update_listbox(_id, _selection):
    if _id == 1:
        _lbx = lbx1
        _log = log1
    if _id == 2:
        _lbx = lbx2
        _log = log2
    if _id == 3:
        _lbx = lbx3
        _log = log3
    if _id == 4:
        _lbx = lbx4
        _log = log4
    if _id == 5:
        _lbx = lbx5
        _log = log5
    if _id == 6:
        _lbx = lbx6
        _log = log6
    if _id == 7:
        _lbx = lbx7
        _log = log7
    if _id == 8:
        _lbx = lbx8
        _log = log8
    if _id == 9:
        _lbx = lbx9
        _log = log9

    _lbx.delete(0, END)
    if _selection == 'Select':
        _lbx.insert(END, [])
        _log.set('')
    else:
        _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, _message = get_data(tag_dict[_selection])
        _log.set(_message)
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
    print('Buffer timestamp:', _buffer_timestamp)
    print('Pressure values:', _pVal)
    if _on_existing is False:
        plt.figure()
        _linestyle = '-'
        _color = 'b'
    else:
        _linestyle, _color = next_plot()

    plt.xlabel('Number of values')
    plt.ylabel('Pressure (Pa)')
    if _buffer_timestamp == 'Invalid Timestamp':
        plt.plot(_pVal, linestyle=_linestyle, color=_color, label=_OPC_Tag + '     ' + 'OPC TS:' + _OPC_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                                                  + '    Buffer TS:' + _buffer_timestamp)
    else:
        plt.plot(_pVal, linestyle=_linestyle, color=_color, label=_OPC_Tag + '     ' + 'OPC TS:' + _OPC_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                                                                  + '    Buffer TS:' + _buffer_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    plt.legend(bbox_to_anchor=(1, 1.16), fontsize='x-small')
    plt.show()


num_datasets = [10, 50, 200, 500]
tags = ['Select', 'MKT', 'MOV60', 'BV61', 'BV62', 'BV63', 'BV64', 'BV65', 'BV66', 'KBS']
tag_dict = {'MKT': 'MKT.NPW.ByteArray', 'MOV60': 'MOV60.NPW.ByteArray', 'BV61': 'BV61.NPW.ByteArray',
            'BV62': 'BV62.NPW.ByteArray', 'BV63': 'BV63.NPW.ByteArray', 'BV64': 'BV64.NPW.ByteArray',
            'BV65': 'BV65.NPW.ByteArray', 'BV66': 'BV66.NPW.ByteArray', 'KBS': 'KBS1.NPW.ByteArray'}

# Connecting to database
while True:
    try:
        print('Connecting to database')
        conn = psycopg2.connect(dbname='postgres', user='postgres', password='@intech#123', host='localhost',
                                port='5432')
    except psycopg2.OperationalError as e:
        print('Unable to connect!\n{0}'.format(e))
    else:
        print('Connected!')
        break

conn.autocommit = True
cursor = conn.cursor()

line_cycle = cycle(['--', ':', '-.', ':', '--', ':', '-.', ':'])
color_cycle = cycle(['k',  'b', 'r',  'y', 'y',  'k', 'b',  'r'])

root = tkinter.Tk()

# Drop down variable
clicked1 = StringVar()
clicked2 = StringVar()
clicked3 = StringVar()
clicked4 = StringVar()
clicked5 = StringVar()
clicked6 = StringVar()
clicked7 = StringVar()
clicked8 = StringVar()
clicked9 = StringVar()
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

clicked1.set(tags[1])
clicked2.set(tags[2])
clicked3.set(tags[3])
clicked4.set(tags[4])
clicked5.set(tags[5])
clicked6.set(tags[6])
clicked7.set(tags[7])
clicked8.set(tags[8])
clicked9.set(tags[9])
clicked15.set(num_datasets[3])

# Radiobutton variable
option_var = IntVar()
option_var.set(1)

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

sbr1 = Scrollbar(fr1, )
sbr2 = Scrollbar(fr2, )
sbr3 = Scrollbar(fr3, )
sbr4 = Scrollbar(fr4, )
sbr5 = Scrollbar(fr5, )
sbr6 = Scrollbar(fr6, )
sbr7 = Scrollbar(fr7, )
sbr8 = Scrollbar(fr8, )
sbr9 = Scrollbar(fr9, )


drop1 = OptionMenu(root, clicked1, *tags, command=partial(update_listbox, 1))
drop2 = OptionMenu(root, clicked2, *tags, command=partial(update_listbox, 2))
drop3 = OptionMenu(root, clicked3, *tags, command=partial(update_listbox, 3))
drop4 = OptionMenu(root, clicked4, *tags, command=partial(update_listbox, 4))
drop5 = OptionMenu(root, clicked5, *tags, command=partial(update_listbox, 5))
drop6 = OptionMenu(root, clicked6, *tags, command=partial(update_listbox, 6))
drop7 = OptionMenu(root, clicked7, *tags, command=partial(update_listbox, 7))
drop8 = OptionMenu(root, clicked8, *tags, command=partial(update_listbox, 8))
drop9 = OptionMenu(root, clicked9, *tags, command=partial(update_listbox, 9))
drop15 = OptionMenu(root, clicked15, *num_datasets)

newPlotButton1 = Button(root, text="Plot New", command=partial(newPlot, False))
extPlotButton1 = Button(root, text="Plot Overlay", command=partial(newPlot, True))
refresh = Button(root, text="Refresh", command=refresh)

R1 = Radiobutton(root, text="Last", variable=option_var, value=1)
R2 = Radiobutton(root, text="Dates", variable=option_var, value=2)

label1 = Label(root, text="timestamps")
label2 = Label(root, text="From")
label3 = Label(root, text="To")
mBox1 = Label(root, textvariable=log1, height=1, width=15, anchor="w")
mBox2 = Label(root, textvariable=log2, height=1, width=15, anchor="w")
mBox3 = Label(root, textvariable=log3, height=1, width=15, anchor="w")
mBox4 = Label(root, textvariable=log4, height=1, width=15, anchor="w")
mBox5 = Label(root, textvariable=log5, height=1, width=15, anchor="w")
mBox6 = Label(root, textvariable=log6, height=1, width=15, anchor="w")
mBox7 = Label(root, textvariable=log7, height=1, width=15, anchor="w")
mBox8 = Label(root, textvariable=log8, height=1, width=15, anchor="w")
mBox9 = Label(root, textvariable=log9, height=1, width=15, anchor="w")


now = datetime.now()
cal_from = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)

T = Text(root, height=25, width=190)

# Widget positions
fr1.grid(row=1, column=0, rowspan=3, columnspan=1, sticky='nw')
fr2.grid(row=1, column=1, rowspan=3, columnspan=1, sticky='nw')
fr3.grid(row=1, column=2, rowspan=3, columnspan=1, sticky='nw')
fr4.grid(row=1, column=3, rowspan=3, columnspan=1, sticky='nw')
fr5.grid(row=1, column=4, rowspan=3, columnspan=1, sticky='nw')
fr6.grid(row=1, column=5, rowspan=3, columnspan=1, sticky='nw')
fr7.grid(row=1, column=6, rowspan=3, columnspan=1, sticky='nw')
fr8.grid(row=1, column=7, rowspan=3, columnspan=1, sticky='nw')
fr9.grid(row=1, column=8, rowspan=3, columnspan=1, sticky='nw')

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

drop1.grid(row=0, column=0)
drop2.grid(row=0, column=1)
drop3.grid(row=0, column=2)
drop4.grid(row=0, column=3)
drop5.grid(row=0, column=4)
drop6.grid(row=0, column=5)
drop7.grid(row=0, column=6)
drop8.grid(row=0, column=7)
drop9.grid(row=0, column=8)
drop15.grid(row=5, column=1)

newPlotButton1.grid(row=5, column=2, sticky='w')
extPlotButton1.grid(row=5, column=3, sticky='w')
refresh.grid(row=5, column=4, sticky='w')

R1.grid(row=5, column=0, sticky='w')
R2.grid(row=6, column=0, sticky='w')

# label1.grid(row=0, column=11)
label2.grid(row=6, column=2)
label3.grid(row=6, column=3)

cal_from.grid(row=7, column=0, columnspan=2)
cal_to.grid(row=7, column=3, columnspan=3)

mBox1.grid(row=4, column=0, sticky='w')
mBox2.grid(row=4, column=1, sticky='w')
mBox3.grid(row=4, column=2, sticky='w')
mBox4.grid(row=4, column=3, sticky='w')
mBox5.grid(row=4, column=4, sticky='w')
mBox6.grid(row=4, column=5, sticky='w')
mBox7.grid(row=4, column=6, sticky='w')
mBox8.grid(row=4, column=7, sticky='w')
mBox9.grid(row=4, column=8, sticky='w')

T.grid(row=8, columnspan=15, sticky='w')

# Connecting listbox and scroll
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
