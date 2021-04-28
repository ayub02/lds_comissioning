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
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CreateLbx:
    def __init__(self, _root, _row, _column, _lbox_width, _key, _node_name):
        self.fr = Frame(_root)
        self.lbx = Listbox(self.fr, font=("Verdana", 8), height=14, width=_lbox_width)
        self.fr.grid(row=_row, column=_column, rowspan=3, columnspan=1, padx=3, sticky='nw')
        self.title = Label(self.fr, text=_key, justify=CENTER)
        self.title.pack(side=TOP, fill="y")
        self.sbr = Scrollbar(self.fr, )
        self.sbr.pack(side=RIGHT, fill="y")
        self.lbx.log = StringVar()
        self.mBox = Label(self.fr, textvariable=self.lbx.log, width=_lbox_width - 1, anchor="w", bg='pale green')
        self.mBox.pack(side=BOTTOM, fill="y")
        self.lbx.pack()
        self.sbr.config(command=self.lbx.yview)
        self.lbx.config(yscrollcommand=self.sbr.set)
        self.lbx.key = _key
        self.lbx.node_name = _node_name
        self.lbx.log.set('Not yet set')
        self.lbx.bind('<<ListboxSelect>>', lbx_select)
        self.lbx.rowNums = []
        self.lbx.header_rows = []

    def update(self):
        self.lbx.delete(0, END)
        self.lbx.rowNums = []
        if self.lbx.header_rows:
            self.lbx.log.set('Found ' + str(len(self.lbx.header_rows)) + ' records')
        else:
            self.lbx.log.set('No records found')

        for _row in reversed(self.lbx.header_rows):
            self.lbx.rowNums.append(_row[0])
            self.lbx.insert(END, _row[1].strftime('%y-%m-%d %H:%M:%S'))  # Important


def read_file():
    print('Reading file')
    _event_type = event_type.get()
    for b in lbx_list:
        b.lbx.header_rows = []
    for i, val in enumerate(body):
        if 'Event' in val:
            val_split = val.split()
            for b in lbx_list:
                if val_split[0] == b.lbx.node_name:
                    try:
                        _timestamp = datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f')
                    except ValueError:
                        print('Warning: Incorrect timestamp encountered in line#{}: {}'.format(i, val_split[1] + " " + val_split[2]))
                        print('Line: {}\n'.format(val))
                    except:
                        print('Warning: Unknown error encountered in line#{}'.format(i))
                        print('Line: {}\n'.format(val))
                    else:
                        if _event_type == 'All':
                            b.lbx.header_rows.append([i, _timestamp, val_split[4]])
                        else:
                            if val_split[4] == _event_type:
                                b.lbx.header_rows.append([i, _timestamp, val_split[4]])
    for b in lbx_list:
        b.update()


def lbx_select(_event):
    global selected_lbx, selected_idx
    _lbx = _event.widget
    _idx = _lbx.curselection()
    if _idx:
        selected_lbx = _lbx
        selected_idx = _idx


def get_buffer(_lbx):
    _idx = _lbx.curselection()[0]
    _start_row = _lbx.rowNums[_idx]
    _timestamps = []
    _values = []
    print(body[_start_row])
    try:
        val_split = body[_start_row].split()
        assert len(val_split) == 5
    except:
        print('Error: Cannot split line#{} into 5 parts'.format(_start_row))
        print('Line: {}\n'.format(body[_start_row]))
        return None, None, None, None, None
    else:
        try:
            _data_timestamp = datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f')
        except:
            print('Error: Incorrect timestamp encountered in line#{}: {}'.format(_start_row, val_split[1] + " " + val_split[2]))
            print('Line: {}'.format(body[_start_row]))
            return None, None, None, None, None
        else:
            _event_type = val_split[4]
            # _end_row =
            for i in range(_start_row + 1, min(_start_row + 1000, len(body)-1)):
                if '---' in body[i]:
                    break
                try:
                    val_split = body[i].split()
                    _timestamps.append(datetime.strptime(val_split[0] + " " + val_split[1], '%d.%m.%Y %H:%M:%S.%f'))
                    _values.append(float(val_split[2]) / 1e5)
                except:
                    print('Error: Unknown problem encountered in line#{}'.format(i))
                    print('Line: {}'.format(body[i]))
                    return None, None, None, None, None
                else:
                    pass
            return _lbx.key, _timestamps, _values, _data_timestamp, _event_type


def next_plot():
    return next(line_cycle), next(color_cycle)


def func_plot(_overlay=False):
    if not selected_lbx:
        print('None selected')
        return
    _lbx = selected_lbx
    _idx = selected_idx
    _station, _timestamps, _pVal, _data_timestamp, _event_type = get_buffer(selected_lbx)
    if _timestamps:
        if pressure_var.get() == 1:
            _pVal_offset = [val - _pVal[0] for val in _pVal]
            _pVal_to_plot = _pVal_offset
        else:
            _pVal_to_plot = _pVal

        if _overlay is False:
            fig, ax = plt.subplots(1, 1)
            _linestyle = '-'
            _color = 'b'
        else:
            fig = plt.gcf()
            ax = plt.gca()
            _linestyle, _color = next_plot()

        if cbox.get() == 1:
            myFmt = mdates.DateFormatter('%H:%M:%S')
            fig.autofmt_xdate()
            ax.set_xlabel('Timestamp H:M:S')
            ax.set_ylabel('Pressure (bar)')
            ax.plot(_timestamps, _pVal_to_plot, linestyle=_linestyle, color=_color,
                    label=_station + '     ' + datetime.strftime(_data_timestamp, '%Y-%m-%d %H:%M:%S.%f')[:-3] + '     ' + _event_type +
                          '     Values: ' + str(len(_pVal_to_plot)))
            ax.legend(fontsize='x-small')
            ax.xaxis.set_major_formatter(myFmt)
        else:
            ax.set_xlabel('Number of values')
            ax.set_ylabel('Pressure (bar)')
            ax.plot(_pVal_to_plot, linestyle=_linestyle, color=_color,
                    label=_station + '     ' + datetime.strftime(_data_timestamp, '%Y-%m-%d %H:%M:%S.%f')[:-3] + '     ' + _event_type +
                          '     Values: ' + str(len(_pVal_to_plot)))
            ax.legend(fontsize='x-small')
        plt.show()
    else:
        print('Error: Plot aborted\n')


file = '../data/Eventdaten.txt'
body = open(file, 'r').readlines()

line_cycle = cycle(['--', ':', '-.', ':', '--', ':', '-.', ':'])
color_cycle = cycle(['k', 'b', 'r', 'y', 'y', 'k', 'b', 'r'])
selected_lbx = None
selected_idx = None
root = tkinter.Tk()

lbox_width = 16
b1 = CreateLbx(root, 0, 0, lbox_width, 'MKT', 'MKT_I')
b2 = CreateLbx(root, 0, 1, lbox_width, 'MOV60', 'MOV60_O')
b3 = CreateLbx(root, 0, 2, lbox_width, 'BV61', 'BV61_O')
b4 = CreateLbx(root, 0, 3, lbox_width, 'BV62', 'BV62_O')
b5 = CreateLbx(root, 0, 4, lbox_width, 'BV63', 'BV63_O')
b6 = CreateLbx(root, 0, 5, lbox_width, 'BV64', 'BV64_O')
b7 = CreateLbx(root, 0, 6, lbox_width, 'BV65', 'BV65_O')
b8 = CreateLbx(root, 0, 7, lbox_width, 'BV66', 'BV66_O')
b9 = CreateLbx(root, 0, 8, lbox_width, 'BV66A', 'BV66A_O')
b10 = CreateLbx(root, 0, 9, lbox_width, 'KBS_3025', 'KBS_I')
b11 = CreateLbx(root, 0, 10, lbox_width, 'KBS_3026', 'KBS_O')
b12 = CreateLbx(root, 3, 0, lbox_width, 'BV69', 'BV69_O')
b13 = CreateLbx(root, 3, 1, lbox_width, 'BV70', 'BV70_O')
b14 = CreateLbx(root, 3, 2, lbox_width, 'BV70A', 'BV70A_O')
b15 = CreateLbx(root, 3, 3, lbox_width, 'BV71', 'BV71_O')
b16 = CreateLbx(root, 3, 4, lbox_width, 'BV72', 'BV72_O')
b17 = CreateLbx(root, 3, 5, lbox_width, 'BV72A', 'BV72A_O')
b18 = CreateLbx(root, 3, 6, lbox_width, 'MOV73', 'MOV73_O')
b19 = CreateLbx(root, 3, 7, lbox_width, 'FSD_4025', 'FSD_I')
b20 = CreateLbx(root, 3, 8, lbox_width, 'FSD_4026', 'FSD_O')
b21 = CreateLbx(root, 3, 9, lbox_width, 'BV74A', 'BV74A_O')
b22 = CreateLbx(root, 3, 10, lbox_width, 'BV75', 'BV75_O')
b23 = CreateLbx(root, 6, 8, lbox_width, 'BV76', 'BV76_O')
b24 = CreateLbx(root, 6, 9, lbox_width, 'MOV77', 'MOV77_O')
b25 = CreateLbx(root, 6, 10, lbox_width, 'MCK_5000A', 'MCK_O')
lbx_list = [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17, b18, b19, b20, b21, b22, b23, b24, b25]

# Radiobutton variable
num_datasets = [100, 500, 1000]
event_type_list = ['All', 'Druckanstieg', 'Druckfall', 'NegativerMittenwert', 'NegativeWelle', 'PositiverMittenwert',
                   'Schwingung', 'PositiveWelle']
option_var = IntVar()
pressure_var = IntVar()
direction_var = IntVar()
cbox = IntVar()
num_records = StringVar()
event_type = StringVar()

option_var.set(1)
pressure_var.set(1)
direction_var.set(1)
num_records.set(num_datasets[1])
event_type.set(event_type_list[0])
# now = datetime.now()
# cal_from = Calendar(root, selectmode="day", year=(now - timedelta(days=1)).year, month=(now - timedelta(days=1)).month,
#                     day=(now - timedelta(days=1)).day)
# cal_to = Calendar(root, selectmode="day", year=now.year, month=now.month, day=now.day)

# R1 = Radiobutton(root, text="Last", variable=option_var, value=1).grid(row=6, column=0, sticky='w')
# R2 = Radiobutton(root, text="Dates", variable=option_var, value=2).grid(row=7, column=0, sticky='w')
# drop_num_records = OptionMenu(root, num_records, *num_datasets).grid(row=6, column=1, sticky='w')
drop_event_type = OptionMenu(root, event_type, *event_type_list)
drop_event_type.grid(row=7, column=0, columnspan=2, sticky='W')

newPlotButton1 = Button(root, text="Plot New", command=partial(func_plot, False)).grid(row=6, column=2, sticky='w')
extPlotButton1 = Button(root, text="Plot Overlay", command=partial(func_plot, True)).grid(row=6, column=3, sticky='w')
refresh = Button(root, text="Refresh", command=read_file).grid(row=6, column=5, sticky='w')
radio_ref = Radiobutton(root, text="Zero ref pressure", variable=pressure_var, value=1).grid(row=6, column=6,
                                                                                             sticky='w')
radio_orig = Radiobutton(root, text="Original pressure", variable=pressure_var, value=2).grid(row=7, column=6,
                                                                                              sticky='NW')
label_event_type = Label(root, text="Event type:").grid(row=6, column=0, sticky='w')
c = Checkbutton(root, text="Xaxis Timestamp", variable=cbox).grid(row=6, column=1, sticky='w')

# label_from = Label(root, text="From").grid(row=7, column=1, columnspan=2)
# label_to = Label(root, text="To").grid(row=7, column=3, columnspan=2)
# cal_from.grid(row=8, column=1, columnspan=2)
# cal_to.grid(row=8, column=3, columnspan=2)

# f = Figure(figsize=(7, 4), dpi=70)
# a = f.add_subplot(111)
# t = np.arange(0.0, 3.0, 0.01)
# s = np.sin(2 * t)
# a.plot(t, s)
#
# dataPlot = FigureCanvasTkAgg(f, master=root)
# dataPlot.get_tk_widget().grid(row=6, column=7, rowspan=3, columnspan=4)

root.mainloop()
