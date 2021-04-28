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
from matplotlib import pyplot as plt
from datetime import datetime, timedelta

#######################################################################################################################
# Only edit this section
station = 'BV72'  # Can be only one from MKT, BV61, BV62, BV63, BV64, BV65, BV66, BV66A, KBSI, KBSO, BV69,
# BV70, BV70A, BV71, BV72, BV72A, FSDI, FSDO, BV74A, BV75, BV76, MCK
start_row = 36414

file = '../data/Eventdaten.txt'
#######################################################################################################################

body = open(file, 'r').readlines()

MKT = []
BV61 = []
BV62 = []
BV63 = []
BV64 = []
BV65 = []
BV66 = []
BV66A = []
KBSI = []
KBSO = []
BV69 = []
BV70 = []
BV70A = []
BV71 = []
BV72 = []
BV72A = []
FSDI = []
FSDO = []
BV74A = []
BV75 = []
BV76 = []
MCKO = []

dict_nodes = {'MKT_I': MKT, 'BV61_O': BV61, 'BV62_O': BV62, 'BV63_O': BV63, 'BV64_O': BV64, 'BV65_O': BV65,
              'BV66_O': BV66, 'BV66A_O': BV66A, 'KBS_I': KBSI, 'KBS_O': KBSO, 'BV69_O': BV69, 'BV70_O': BV70,
              'BV70A_O': BV70A, 'BV71_O': BV71, 'BV72_O': BV72, 'BV72A_O': BV72A, 'FSD_I': FSDI, 'FSD_O': FSDO,
              'BV74A_O': BV74A, 'BV75_O': BV75, 'BV76_O': BV76, 'MCK_O': MCKO}

for i, val in enumerate(body):
    if 'Event' in val:
        val_split = val.split()
        for key, node in dict_nodes.items():
            if val_split[0] == key:
                dict_nodes[key].append([i, datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'),
                                        val_split[4]])

# buffer_timestamps = []
# buffer_values = []
# for i in range(start_row+1, start_row+501):
#     val_split = body[i].split()
#     if '---' in val_split[0]:
#         break
#     buffer_timestamps.append(datetime.strptime(val_split[0] + " " + val_split[1], '%d.%m.%Y %H:%M:%S.%f'))
#     buffer_values.append(float(val_split[2])/1e5)
#
# title = body[start_row][:-1] + ' with ' + str(len(buffer_values)) + ' values...'
# plt.plot(buffer_timestamps, buffer_values, color='blue', label=title)
# plt.legend()
# plt.gcf().autofmt_xdate()
# myFmt = mdates.DateFormatter('%H:%M:%S')
# plt.gca().xaxis.set_major_formatter(myFmt)
# plt.show()
