import os
import tkinter
from tkinter import *
from tkcalendar import *
import configparser
import psycopg2
import datetime
import pandas as pd
import numpy as np
from psycopg2 import sql
from itertools import cycle
from functools import partial
from datetime import datetime
from matplotlib import pyplot as plt
import matplotlib.dates as mdates


def export_wrapper():
    new_plot(_plot=False, _export=True)


def plot_wrapper():
    new_plot(_plot=True, _export=False)


def new_plot(_plot=False, _export=False):
    _tag = var_tag.get()
    print('Tag:   ', _tag)

    from_month, from_day, from_year = cal_from.get_date().split('/')
    _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), int(var_fromHour.get()),
                          int(var_fromMinute.get()), 0)

    to_month, to_day, to_year = cal_to.get_date().split('/')
    _to_date = datetime(int('20' + to_year), int(to_month), int(to_day), int(var_toHour.get()),
                        int(var_toMinute.get()), 0)

    _query = sql.SQL(
        "SELECT * FROM {} WHERE itemid= %s AND itemtimestamp BETWEEN %s AND %s ORDER BY itemtimestamp DESC;").format(sql.Identifier(table))
    cursor.execute(_query, (_tag, _from_date, _to_date))
    _values = []
    _timestamps = []
    _time_num = []
    _interval = []
    _seconds = []
    _gradient = []
    _rows = cursor.fetchall()
    if _rows:
        for i in range(len(_rows) - 1):
            print(_rows[i])
            _time_num.append((_rows[i][2] - _rows[-1][2]).total_seconds())
            if ',' in _rows[i][1]:
                _values.append(float(_rows[i][1].replace(',', '')))
            else:
                _values.append(float(_rows[i][1]))
            _timestamps.append(_rows[i][2])
            _seconds.append((_rows[i][2]-_rows[-2][2]).total_seconds())
            _interval.append((_rows[i][2] - _rows[i + 1][2]).total_seconds())
    else:
        raise ValueError('No records returned from OPC')
    print(_tag, '        ', np.max(np.asarray(_values)), '        ', np.min(np.asarray(_values)))

    if _plot:
        if CheckVar2.get() == 1:
            plt.figure(1)
            plt.plot(_timestamps, _interval, label=_tag + '  Avg:' + str(round(np.average(np.asarray(_interval)), 2)), marker = 'o')
            plt.xlabel('Timestamps (HH:MM:SS)')
            plt.ylabel('Polling interval (seconds)')
            plt.legend(bbox_to_anchor=(0.4, 1), fontsize='x-small')
            plt.gcf().autofmt_xdate()
            myFmt = mdates.DateFormatter('%H:%M:%S')
            plt.gca().xaxis.set_major_formatter(myFmt)

        if CheckVar1.get() == 1:
            if pressure_var.get() == 1:
                print(_values)
                print(_time_num)
                _pVal_to_plot = [val - _values[-1] for val in _values]
            else:
                _pVal_to_plot = _values

            plt.figure(2)
            _min = str(round(np.min(np.asarray(_pVal_to_plot)), 1))
            _max = str(round(np.max(np.asarray(_pVal_to_plot)), 1))
            _avg = str(round(np.average(np.asarray(_pVal_to_plot)), 1))
            _std = str(round(np.std(np.asarray(_pVal_to_plot)), 4))
            print('Number of records', len(_pVal_to_plot))
            plt.plot(_timestamps, _pVal_to_plot, marker='.', markerfacecolor='lime', markeredgecolor='lime', markersize=2,
                     label=_tag + '  Max:' + _max + '  Min:' + _min + '  Std:' + _std + '  Avg:' + _avg)
            plt.xlabel('Timestamps (HH:MM:SS)')
            plt.ylabel('Value')
            plt.legend(bbox_to_anchor=(0.4, 1), fontsize='x-small')
            plt.gcf().autofmt_xdate()
            myFmt = mdates.DateFormatter('%H:%M:%S')
            plt.gca().xaxis.set_major_formatter(myFmt)

        if CheckVar3.get() == 1:
            _pVal_to_plot = _gradient

            plt.figure(3)
            _min = str(round(np.min(np.asarray(_pVal_to_plot)), 1))
            _max = str(round(np.max(np.asarray(_pVal_to_plot)), 1))
            _avg = str(round(np.average(np.asarray(_pVal_to_plot)), 1))
            _std = str(round(np.std(np.asarray(_pVal_to_plot)), 4))
            print('Number of records', len(_pVal_to_plot))
            plt.plot(_timestamps, _pVal_to_plot, label=_tag + '  Max:' + _max + '  Min:' + _min + '  Std:' + _std + '  Avg:' + _avg)
            plt.xlabel('Timestamps (HH:MM:SS)')
            plt.ylabel('Gradient (bar/s)')
            plt.legend(bbox_to_anchor=(0.4, 1), fontsize='x-small')
            plt.gcf().autofmt_xdate()
            myFmt = mdates.DateFormatter('%H:%M:%S')
            plt.gca().xaxis.set_major_formatter(myFmt)

        plt.show()

    if _export:
        _dict = {'Timestamps': _timestamps, 'Seconds': _seconds, 'Values':_values}
        _df = pd.DataFrame(data=_dict)
        print(_df)
        _filename = (_tag + '__' + 'from' + '__' + _from_date.strftime('%Y_%m_%d__%H_%M') + '__' + 'to' + '__' +
                     _to_date.strftime('%Y_%m_%d__%H_%M')).replace('.', '_')
        _filename = _filename + '.csv'
        _path = '../output/'
        print(_filename)
        if os.path.exists(_path+_filename):
            os.remove(_path+_filename)
            print('Removed ', _filename)
        else:
            _df.to_csv(_path+_filename, index=False)
            print('File write successful \t\t', _filename)


num_pts = [100, 1000, 5000, 10000, 100000, 1000000]
hours = range(0, 24)
minutes = range(0, 60)

tags = (pd.read_excel('../data/instrument_tags.xlsx', sheet_name=0)['Tags']).to_list()

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

now = datetime.now()

pressure_var = IntVar()
pressure_var.set(1)

var_fromHour = StringVar()
var_fromHour.set(now.hour)

var_toHour = StringVar()
var_toHour.set(now.hour)

var_fromMinute = StringVar()
var_fromMinute.set(now.minute)

var_toMinute = StringVar()
var_toMinute.set(now.minute)

var_tag = StringVar()
var_tag.set(tags[0])

CheckVar1 = IntVar()
CheckVar2 = IntVar()
CheckVar3 = IntVar()
CheckVar1.set(1)

check1 = Checkbutton(root, text="Values", variable=CheckVar1, onvalue=1, offvalue=0, width=10).grid(row=0, column=4, sticky='w')
check2 = Checkbutton(root, text="Poll rate", variable=CheckVar2, onvalue=1, offvalue=0, width=10).grid(row=0, column=5, sticky='w')
check3 = Checkbutton(root, text="Gradient", variable=CheckVar3, onvalue=1, offvalue=0, width=10).grid(row=0, column=6, sticky='w')

radio_ref = Radiobutton(root, text="Zero reference pressure", variable=pressure_var, value=1).grid(row=0, column=9, sticky='w')
radio_orig = Radiobutton(root, text="Original pressure", variable=pressure_var, value=2).grid(row=1, column=9, sticky='w')

label_from = Label(root, text="From", justify=CENTER).grid(row=1, column=0, columnspan=4)
label_to = Label(root, text="To", justify=CENTER).grid(row=1, column=4, columnspan=4)
label_fromHour = Label(root, text="Hour").grid(row=2, column=0, sticky='w')
label_fromMinute = Label(root, text="Min").grid(row=2, column=2, sticky='w')
label_toHour = Label(root, text="Hour").grid(row=2, column=4, sticky='w')
label_toMinute = Label(root, text="Min").grid(row=2, column=6, sticky='w')
label_tag = Label(root, text="Tag").grid(row=0, column=0, sticky='w')

drop_fromHour = OptionMenu(root, var_fromHour, *hours).grid(row=2, column=1, sticky='w')
drop_fromMinute = OptionMenu(root, var_fromMinute, *minutes).grid(row=2, column=3, sticky='w')
drop_toHour = OptionMenu(root, var_toHour, *hours).grid(row=2, column=5, sticky='w')
drop_toMinute = OptionMenu(root, var_toMinute, *minutes).grid(row=2, column=7, sticky='w')

drop_tag = OptionMenu(root, var_tag, *tags)
drop_tag.grid(row=0, column=1, columnspan=3, sticky='w')
drop_tag.config(width=29)

plotButton = Button(root, text="Plot", command=plot_wrapper, width=20).grid(row=2, column=9, sticky='w')
exportButton = Button(root, text="Export", command=export_wrapper, width=20).grid(row=3, column=9, sticky='w')

cal_from = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day - 1)
cal_from.grid(row=3, column=0, columnspan=4)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)
cal_to.grid(row=3, column=4, columnspan=4)

root.mainloop()
