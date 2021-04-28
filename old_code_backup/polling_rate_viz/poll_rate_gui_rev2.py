import tkinter
from tkinter import *
from tkcalendar import *
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


def new_plot():
    _tag = var_tag.get()
    print('Tag:   ', _tag)

    from_month, from_day, from_year = cal_from.get_date().split('/')
    _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), int(var_fromHour.get()),
                          int(var_fromMinute.get()), 0)

    to_month, to_day, to_year = cal_to.get_date().split('/')
    _to_date = datetime(int('20' + to_year), int(to_month), int(to_day), int(var_toHour.get()),
                        int(var_toMinute.get()), 0)

    # print("From date:", _from_date)
    # print("To date:  ", _to_date)
    _query = sql.SQL(
        "SELECT * FROM mfmdata WHERE itemid= %s AND itemtimestamp BETWEEN %s AND %s ORDER BY itemtimestamp DESC;")
    cursor.execute(_query, (_tag, _from_date, _to_date))
    _values = []
    _timestamps = []
    _interval = []
    _rows = cursor.fetchall()
    if _rows:
        for i in range(len(_rows) - 1):
            _values.append(float(_rows[i][1]))
            _timestamps.append(_rows[i][2])
            _interval.append((_rows[i][2] - _rows[i + 1][2]).total_seconds())
    else:
        raise ValueError('No records returned from OPC')
    print(_tag, '        ', np.max(np.asarray(_values)), '        ', np.min(np.asarray(_values)))

    plt.figure(1)
    plt.plot(_timestamps, _interval, label=_tag + '  Avg:' + str(round(np.average(np.asarray(_interval)), 2)))
    plt.xlabel('Timestamps (HH:MM)')
    plt.ylabel('Polling interval (seconds)')
    plt.legend(bbox_to_anchor=(0.4, 1), fontsize='x-small')
    plt.gcf().autofmt_xdate()
    myFmt = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(myFmt)

    plt.figure(2)
    _min = str(round(np.min(np.asarray(_values)), 1))
    _max = str(round(np.max(np.asarray(_values)), 1))
    _avg = str(round(np.average(np.asarray(_values)), 1))
    _std = str(round(np.std(np.asarray(_values)), 4))
    plt.plot(_timestamps, _values, label=_tag + '  Max:' + _max + '  Min:' + _min + '  Std:' + _std + '  Avg:' + _avg)
    plt.xlabel('Timestamps (HH:MM)')
    plt.ylabel('Value')
    plt.legend(bbox_to_anchor=(0.4, 1), fontsize='x-small')
    plt.gcf().autofmt_xdate()
    myFmt = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(myFmt)

    plt.show()


num_pts = [100, 1000, 5000, 10000, 100000, 1000000]
hours = range(0, 24)
minutes = range(0, 60)

tags = (pd.read_excel('../data/instrument_tags_POC.xlsx', sheet_name=0)['Tags']).to_list()

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

root = tkinter.Tk()

now = datetime.now()

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

plotButton = Button(root, text="Plot", command=new_plot).grid(row=2, column=9)

cal_from = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day - 1)
cal_from.grid(row=3, column=0, columnspan=4)
cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)
cal_to.grid(row=3, column=4, columnspan=4)
root.mainloop()
