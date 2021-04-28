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
    print('Showing for tag ', _tag)

    from_month, from_day, from_year = cal.get_date().split('/')
    _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), int(var_hour.get()), int(var_minute.get()), 0)


    _query = sql.SQL(
        "SELECT * FROM mfmdata WHERE itemid= %s AND itemtimestamp <= %s ORDER BY itemtimestamp DESC LIMIT %s;")
    cursor.execute(_query, (_tag, _from_date, int(var_num_pts.get()),))
    _values = []
    _timestamps = []
    _interval = []
    _rows = cursor.fetchall()
    for i in range(len(_rows)-1):
        _values.append(float(_rows[i][1]))
        _timestamps.append(_rows[i][2])
        _interval.append((_rows[i][2]-_rows[i+1][2]).total_seconds())
    # plt.figure()
    plt.plot(_timestamps, _interval, label=_tag+'  Avg:'+str(round(np.average(np.asarray(_interval)), 1)))
    plt.xlabel('Timestamps (HH:MM)')
    plt.ylabel('Polling interval (seconds)')
    plt.legend(bbox_to_anchor=(0.4, 1), fontsize='x-small')
    plt.gcf().autofmt_xdate()
    myFmt = mdates.DateFormatter('%H:%M')
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.show()


num_pts = [100, 1000, 5000, 10000, 100000, 1000000]
hours = range(0, 24)
minutes = range(0, 60)

tags = ['MQTT.MKT.PT_2003', 'MKTPLC.AB.Global.FT_2080_M', 'MKTPLC.AB.Global.TT_2003', 'MKTPLC.AB.Global.TT_FT_2080',
        'MQTT.MOV60.PT_2084',
        'MQTT.BV61.PT_61', 'MQTT.BV62.PT_62', 'MQTT.BV63.PT_63', 'MQTT.BV64.PT_64', 'MQTT.BV65.PT_65', 'MQTT.BV66.PT_66',
        'KBSPLC.HC900.Global.PT_3010',
        'MQTT.KBS1.PT_3025', 'KBSPLC.HC900.Global.FT_3010_M', 'KBSPLC.HC900.Global.TT_3011']

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

var_hour = StringVar()
var_minute = StringVar()
var_num_pts = StringVar()
var_tag = StringVar()

now = datetime.now()

var_hour.set(now.hour)
var_minute.set(now.minute)
var_num_pts.set(num_pts[2])
var_tag.set(tags[0])

label_hour = Label(root, text="Hour")
label_minute = Label(root, text="Min")
label_num_pts = Label(root, text="Num Pts")
label_tag = Label(root, text="Tag")

drop_hour = OptionMenu(root, var_hour, *hours)
drop_minute = OptionMenu(root, var_minute, *minutes)
drop_num_pts = OptionMenu(root, var_num_pts, *num_pts)
drop_tag = OptionMenu(root, var_tag, *tags)

plotButton = Button(root, text="Plot", command=new_plot)

cal = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)

label_hour.grid(row=1, column=0, sticky='w')
label_minute.grid(row=1, column=2, sticky='w')
label_num_pts.grid(row=1, column=4, sticky='w')
label_tag.grid(row=0, column=0, sticky='w')

drop_hour.grid(row=1, column=1, sticky='w')
drop_minute.grid(row=1, column=3, sticky='w')
drop_num_pts.grid(row=1, column=5, sticky='w')
drop_tag.grid(row=0, column=1, sticky='w')

plotButton.grid(row=1, column=6)

cal.grid(row=2, column=0, columnspan=4)

root.mainloop()

