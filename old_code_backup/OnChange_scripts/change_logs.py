import os
import tkinter
import psycopg2
import datetime
import pandas as pd
from tkinter import *
from tkcalendar import *
from psycopg2 import sql
from itertools import cycle
from functools import partial
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


def gen_logs():
    _data = pd.read_excel('../data/valves_pumps_tags.xlsx', sheet_name=0)
    _pcvTags = [val for val in _data['pcvs'].to_list() if val == val]
    _pumpTags = [val for val in _data['pumps'].to_list() if val == val]
    _stationValveTags = [val for val in _data['stationValves'].to_list() if val == val]
    _blockValveTags = [val for val in _data['blockValves'].to_list() if val == val]

    _tags = _pumpTags + _stationValveTags + _blockValveTags

    from_month, from_day, from_year = cal_from.get_date().split('/')
    _from_date = datetime(int('20' + from_year), int(from_month), int(from_day), int(var_fromHour.get()),
                          int(var_fromMinute.get()), 0)

    to_month, to_day, to_year = cal_to.get_date().split('/')
    _to_date = datetime(int('20' + to_year), int(to_month), int(to_day), int(var_toHour.get()),
                        int(var_toMinute.get()), 0)

    print('Fetching records ... ')
    _query = sql.SQL(
        "SELECT * FROM mfmdata WHERE itemid IN %s AND itemtimestamp BETWEEN %s AND %s ORDER BY itemtimestamp DESC;")
    cursor.execute(_query, (tuple(_tags), _from_date, _to_date))
    _values = []
    _timestamps = []
    _interval = []
    _rows = cursor.fetchall()
    _num_records = len(_rows)

    if _rows:
        print('Fetched ', _num_records, 'records')
        print('*************** Logs start ***************')
        _num_records_to_print = _num_records
        if _num_records_to_print > 1000:
            _num_records_to_print = 1000

        for i in range(_num_records_to_print):
            row = _rows[i]
            print(row[2], '\t', row[0], '\t\t', row[1], '\t\t', row[3], '\t\t\t', '[', i+1, '/', _num_records, ']')
        print('*************** Logs end *************** ')
    else:
        print('****************************')
        print('No records returned from OPC')
        print('****************************')


hours = range(0, 24)
minutes = range(0, 60)

while True:
    try:
        print('Connecting to database ...')
        conn = psycopg2.connect(dbname='mfmdata6Dec', user='postgres', password='@intech#123', host='10.1.17.149',
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

var_pcv = IntVar()
var_pump = IntVar()
var_stationValve = IntVar()
var_blockValve = IntVar()
var_pcv.set(1)
var_pump.set(1)
var_stationValve.set(1)
var_blockValve.set(1)

printButton = Button(root, text='Print Logs', width=40, command=gen_logs)
printButton.grid(row=2, column=0, columnspan=8)

check_pcv = Checkbutton(root, text="PCVs", variable=var_pcv, onvalue=1, offvalue=0).grid(row=0, column=0, columnspan=2, sticky='w')
check_pump = Checkbutton(root, text="Pumps", variable=var_pump, onvalue=1, offvalue=0).grid(row=0, column=2, columnspan=2, sticky='w')
check_stationValve = Checkbutton(root, text="Station Valves", variable=var_stationValve, onvalue=1, offvalue=0).grid(row=0, column=4, columnspan=2, sticky='w')
check_blockValve = Checkbutton(root, text="Block Valves", variable=var_blockValve, onvalue=1, offvalue=0).grid(row=0, column=6, columnspan=2, sticky='w')

label_from = Label(root, text="From", justify=CENTER).grid(row=3, column=0, columnspan=4)
label_to = Label(root, text="To", justify=CENTER).grid(row=3, column=4, columnspan=4)
label_fromHour = Label(root, text="Hour").grid(row=4, column=0, sticky='w')
label_fromMinute = Label(root, text="Min").grid(row=4, column=2, sticky='w')
label_toHour = Label(root, text="Hour").grid(row=4, column=4, sticky='w')
label_toMinute = Label(root, text="Min").grid(row=4, column=6, sticky='w')

drop_fromHour = OptionMenu(root, var_fromHour, *hours).grid(row=4, column=1, sticky='w')
drop_fromMinute = OptionMenu(root, var_fromMinute, *minutes).grid(row=4, column=3, sticky='w')
drop_toHour = OptionMenu(root, var_toHour, *hours).grid(row=4, column=5, sticky='w')
drop_toMinute = OptionMenu(root, var_toMinute, *minutes).grid(row=4, column=7, sticky='w')

today = datetime.now()
yesterday = datetime.now() + timedelta(days=0)

cal_from = Calendar(root, selectmode="day", year=yesterday.year, month=yesterday.month, day=yesterday.day)
cal_from.grid(row=5, column=0, columnspan=4)
cal_to = Calendar(root, selectmode="day", year=today.year, month=today.month, day=today.day)
cal_to.grid(row=5, column=4, columnspan=4)

root.mainloop()
