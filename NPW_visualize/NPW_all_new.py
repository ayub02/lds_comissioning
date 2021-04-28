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
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np


class CreateLbx:
    def __init__(self, _root, _row, _column, _lbox_width, _key, _dict_tag):
        self._fr = Frame(_root)
        self._lbx = Listbox(self._fr, font=("Verdana", 8), height=14, width=_lbox_width)
        self._fr.grid(row=_row, column=_column, rowspan=3, columnspan=1, padx=3, sticky='nw')
        self._title = Label(self._fr, text=_key, justify=CENTER)
        self._title.pack(side=TOP, fill="y")
        self._sbr = Scrollbar(self._fr, )
        self._sbr.pack(side=RIGHT, fill="y")
        self._log = StringVar()
        self._mBox = Label(self._fr, textvariable=self._log, width=_lbox_width - 1, anchor="w", bg='pale green')
        self._mBox.pack(side=BOTTOM, fill="y")
        self._lbx.pack()
        self._sbr.config(command=self._lbx.yview)
        self._lbx.config(yscrollcommand=self._sbr.set)
        self._lbx.key = _key
        self._lbx.tag = _dict_tag[self._lbx.key]
        self._log.set('Not yet set')
        self._lbx.bind('<<ListboxSelect>>', lbx_select)

    def update(self):
        self._lbx.delete(0, END)
        _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, _message = get_data(self._lbx.tag)
        self._log.set(_message)
        _dfData = []
        if _opcTag:
            for i in range(len(_opcTag)):
                _dfData.append([_opcTag[i], _rawBuffer[i], _opcTimestamp[i], _pVal[i], _bufferTimestamp[i]])
            self._lbx.df = pd.DataFrame(_dfData, columns=['OPC_Tag', 'Buffer', 'OPC_timestamp', 'Pressure_values',
                                                          'Buffer_timestamp'])
            for val in self._lbx.df['OPC_timestamp']:
                self._lbx.insert(END, val.strftime('%y-%m-%d %H:%M:%S'))  # Important


def lbx_select(_event):
    global selected_lbx, selected_idx
    _lbx = _event.widget
    _idx = _lbx.curselection()
    if _idx:
        selected_lbx = _lbx
        selected_idx = _idx


def get_data(_tag):
    if option_var.get() == 1:
        _query = sql.SQL("SELECT * FROM {} where itemid= %s ORDER BY itemtimestamp DESC LIMIT %s;").format(
            sql.Identifier(table))
        print(datetime.now(), '\t', _tag, '\tFetching data .........')
        cursor.execute(_query, (_tag, int(num_records.get())))

    if option_var.get() == 2:
        from_month, from_day, from_year = cal_from.get_date().split('/')
        to_month, to_day, to_year = cal_to.get_date().split('/')

        _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), 0, 0, 0)
        _to_date = datetime(int('20' + to_year), int(to_month), int(to_day), 23, 59, 59)
        if _from_date >= _to_date:
            return None, None, None, None, None, 'Start date cannot be greater than end date'

        _query = sql.SQL(
            "SELECT * FROM {} WHERE itemid= %s AND itemtimestamp BETWEEN %s AND %s ORDER BY itemtimestamp DESC;").format(
            sql.Identifier(table))
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
        return _opcTag, _rawBuffer, _opcTimestamp, _pVal, _bufferTimestamp, "Found " + str(
            len(_opcTag)) + " records"
    return None, None, None, None, None, "No records found"


def decode_time(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    hour_offset = 5  # Hour offset implemented!!!
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


def decode(_buffer_len, _buffer):
    assert len(_buffer) == _buffer_len
    _pVal = []
    for i in range(8, _buffer_len, 2):
        _pVal.append(((_buffer[i] << 8) + _buffer[i + 1]) / 500)
    return _pVal


def newPlot(_overlay, _export=False):
    if not selected_lbx:
        print('None selected')
        return
    _lbx = selected_lbx
    _idx = selected_idx
    if _export:
        _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%y-%m-%d %H:%M:%S'))
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
        if os.path.exists(_path + _filename):
            os.remove(_path + _filename)
            print('Removed ', _filename)
        else:
            _df.to_csv(_path + _filename, index=False)
            print('File write successful \t\t', _filename)

    else:
        _pd_Timestamp = pd.Timestamp(datetime.strptime(_lbx.get(_idx), '%y-%m-%d %H:%M:%S'))
        func_plot(_lbx.df['OPC_Tag'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Buffer'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['OPC_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Pressure_values'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _lbx.df['Buffer_timestamp'][_lbx.df['OPC_timestamp'] == _pd_Timestamp].tolist()[0],
                  _on_existing=_overlay)


def export_func():
    newPlot(False, True)


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
        if _val <= _pmin + abs(_dP * 0.8):
            _p80 = _val
            _i80 = i
            break

    for i, _val in enumerate(_pVal_to_plot):
        if _val <= _pmin + abs(_dP * 0.3):
            _p30 = _val
            _i30 = i
            break

    if _i80 - _i30 == 0:
        _gradient = 99999
    else:
        _gradient = (_p80 - _p30) / (_i80 - _i30) / 0.1

    if _on_existing is False:
        plt.figure()
        _linestyle = '-'
        _color = 'b'
    else:
        _linestyle, _color = next_plot()

    plt.xlabel('Number of values')
    plt.ylabel('Pressure (bar)')
    if _buffer_timestamp == 'Invalid Timestamp':
        plt.plot(_pVal_to_plot, linestyle=_linestyle, color=_color,
                 label='dP: ' + str(round(_dP, 3)) + ' bar   ' + 'grad: ' + str(round(_gradient, 3)) + '   '
                       + _OPC_Tag + '     ' + 'OPC TS:'
                       + _OPC_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                       + '    Buffer TS:' + _buffer_timestamp)
        plt.plot([_i80, _i30], [_p80, _p30], color='yellow', linestyle='--')
    else:
        plt.plot(_pVal_to_plot, linestyle=_linestyle, color=_color,
                 label='dP: ' + str(round(_dP, 3)) + ' bar   ' + 'grad: ' + str(round(_gradient, 3)) + '   '
                       + _OPC_Tag + '     ' + 'OPC TS:'
                       + _OPC_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                       + '    Buffer TS:' + _buffer_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        plt.plot([_i80, _i30], [_p80, _p30], color='yellow', linestyle='--')
    plt.legend(fontsize='x-small')
    plt.show()


def update_listbox():
    b1.update()
    b2.update()
    b3.update()
    b4.update()
    b5.update()
    b6.update()
    b7.update()
    b8.update()
    b9.update()
    b10.update()
    b11.update()
    b12.update()
    b13.update()
    b14.update()
    b15.update()
    b16.update()
    b17.update()
    b18.update()
    b19.update()
    b20.update()
    b21.update()
    b22.update()
    b23.update()
    b24.update()
    b25.update()


config = configparser.ConfigParser()
config.read('../config/database.ini')
host = config['postgresql']['host']
database = config['postgresql']['database']
user = config['postgresql']['user']
password = config['postgresql']['password']
table = config['postgresql']['table']
port = config['postgresql']['port']

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

dict_tags = {'MKT': 'NPW_array_PT_2003', 'MOV60': 'NPW_array_PT_2084', 'BV61': 'NPW_array_PT_61', 'BV62': 'NPW_array_PT_62',
             'BV63': 'NPW_array_PT_63', 'BV64': 'NPW_array_PT_64', 'BV65': 'NPW_array_PT_65',
             'BV66': 'NPW_array_PT_66', 'BV66A': 'NPW_array_PT_66A', 'KBS_3025': 'NPW_array_PT_3025',
             'KBS_3026': 'NPW_array_PT_3026', 'BV69': 'NPW_array_PT_69', 'BV70': 'NPW_array_PT_70',
             'BV70A': 'NPW_array_PT_70A', 'BV71': 'NPW_array_PT_71', 'BV72': 'NPW_array_PT_72',
             'BV72A': 'NPW_array_PT_72A', 'MOV73': 'NPW_array_PT_4013', 'FSD_4025': 'NPW_array_PT_4025', 'FSD_4026': 'NPW_array_PT_4026',
             'BV74A': 'NPW_array_PT_74A', 'BV75': 'NPW_array_PT_75', 'BV76': 'NPW_array_PT_76', 'MOV77': 'NPW_array_PT_5013',
             'MCK_5000A': 'NPW_array_PT_5000A'}

line_cycle = cycle(['--', ':', '-.', ':', '--', ':', '-.', ':'])
color_cycle = cycle(['k', 'b', 'r', 'y', 'y', 'k', 'b', 'r'])
selected_lbx = None
selected_idx = None
root = tkinter.Tk()

lbox_width = 16
b1 = CreateLbx(root, 0, 0, lbox_width, 'MKT', dict_tags)
b2 = CreateLbx(root, 0, 1, lbox_width, 'MOV60', dict_tags)
b3 = CreateLbx(root, 0, 2, lbox_width, 'BV61', dict_tags)
b4 = CreateLbx(root, 0, 3, lbox_width, 'BV62', dict_tags)
b5 = CreateLbx(root, 0, 4, lbox_width, 'BV63', dict_tags)
b6 = CreateLbx(root, 0, 5, lbox_width, 'BV64', dict_tags)
b7 = CreateLbx(root, 0, 6, lbox_width, 'BV65', dict_tags)
b8 = CreateLbx(root, 0, 7, lbox_width, 'BV66', dict_tags)
b9 = CreateLbx(root, 0, 8, lbox_width, 'BV66A', dict_tags)
b10 = CreateLbx(root, 0, 9, lbox_width, 'KBS_3025', dict_tags)
b11 = CreateLbx(root, 0, 10, lbox_width, 'KBS_3026', dict_tags)
b12 = CreateLbx(root, 3, 0, lbox_width, 'BV69', dict_tags)
b13 = CreateLbx(root, 3, 1, lbox_width, 'BV70', dict_tags)
b14 = CreateLbx(root, 3, 2, lbox_width, 'BV70A', dict_tags)
b15 = CreateLbx(root, 3, 3, lbox_width, 'BV71', dict_tags)
b16 = CreateLbx(root, 3, 4, lbox_width, 'BV72', dict_tags)
b17 = CreateLbx(root, 3, 5, lbox_width, 'BV72A', dict_tags)
b18 = CreateLbx(root, 3, 6, lbox_width, 'MOV73', dict_tags)
b19 = CreateLbx(root, 3, 7, lbox_width, 'FSD_4025', dict_tags)
b20 = CreateLbx(root, 3, 8, lbox_width, 'FSD_4026', dict_tags)
b21 = CreateLbx(root, 3, 9, lbox_width, 'BV74A', dict_tags)
b22 = CreateLbx(root, 3, 10, lbox_width, 'BV75', dict_tags)
b23 = CreateLbx(root, 6, 8, lbox_width, 'BV76', dict_tags)
b24 = CreateLbx(root, 6, 9, lbox_width, 'MOV77', dict_tags)
b25 = CreateLbx(root, 6, 10, lbox_width, 'MCK_5000A', dict_tags)

# Radiobutton variable
num_datasets = [100, 500, 1000]
option_var = IntVar()
pressure_var = IntVar()
direction_var = IntVar()
num_records = StringVar()

option_var.set(1)
pressure_var.set(1)
direction_var.set(1)
num_records.set(num_datasets[1])
now = datetime.now()
cal_from = Calendar(root, selectmode="day", year=(now - timedelta(days=1)).year, month=(now - timedelta(days=1)).month,
                    day=(now - timedelta(days=1)).day)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)

R1 = Radiobutton(root, text="Last", variable=option_var, value=1).grid(row=6, column=0, sticky='w')
R2 = Radiobutton(root, text="Dates", variable=option_var, value=2).grid(row=7, column=0, sticky='w')
drop_num_records = OptionMenu(root, num_records, *num_datasets).grid(row=6, column=1, sticky='w')
newPlotButton1 = Button(root, text="Plot New", command=partial(newPlot, False)).grid(row=6, column=2, sticky='w')
extPlotButton1 = Button(root, text="Plot Overlay", command=partial(newPlot, True)).grid(row=6, column=3, sticky='w')
exportExcel = Button(root, text="Export csv", command=export_func).grid(row=6, column=4, sticky='w')
refresh = Button(root, text="Refresh", command=update_listbox).grid(row=6, column=5, sticky='w')
radio_ref = Radiobutton(root, text="Zero ref pressure", variable=pressure_var, value=1).grid(row=6, column=6,
                                                                                             sticky='w')
radio_orig = Radiobutton(root, text="Original pressure", variable=pressure_var, value=2).grid(row=7, column=6,
                                                                                              sticky='w')
label_from = Label(root, text="From").grid(row=7, column=1, columnspan=2)
label_to = Label(root, text="To").grid(row=7, column=3, columnspan=2)
cal_from.grid(row=8, column=1, columnspan=2)
cal_to.grid(row=8, column=3, columnspan=2)

root.mainloop()
