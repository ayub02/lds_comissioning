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
station = 'BV66'             # Can be only one from MKT, BV61, BV62, BV63, BV64, BV65, BV66, BV66A, KBSI, KBSO, BV69,
                            # BV70, BV70A, BV71, BV72, BV72A, FSDI, FSDO, BV74A, BV75, BV76, MCK
start_row = 7286840
file = '../data/Eventdaten.txt'
#######################################################################################################################

body = open(file, 'r').readlines()
tags = ['MKT_I', 'BV61_O', 'BV62_O', 'BV63_O', 'BV64_O', 'BV65_O', 'BV66_O', 'BV66A_O', 'KBS_O']

MKT_rowIDs = []
BV61_rowIDs = []
BV62_rowIDs = []
BV63_rowIDs = []
BV64_rowIDs = []
BV65_rowIDs = []
BV66_rowIDs = []
BV66A_rowIDs = []
KBSI_rowIDs = []
KBSO_rowIDs = []
BV69_rowIDs = []
BV70_rowIDs = []
BV70A_rowIDs = []
BV71_rowIDs = []
BV72_rowIDs = []
BV72A_rowIDs = []
FSDI_rowIDs = []
FSDO_rowIDs = []
BV74A_rowIDs = []
BV75_rowIDs = []
BV76_rowIDs = []
MCKO_rowIDs = []

MKT_timestamps = []
BV61_timestamps = []
BV62_timestamps = []
BV63_timestamps = []
BV64_timestamps = []
BV65_timestamps = []
BV66_timestamps = []
BV66A_timestamps = []
KBSI_timestamps = []
KBSO_timestamps = []
BV69_timestamps = []
BV70_timestamps = []
BV70A_timestamps = []
BV71_timestamps = []
BV72_timestamps = []
BV72A_timestamps = []
FSDI_timestamps = []
FSDO_timestamps = []
BV74A_timestamps = []
BV75_timestamps = []
BV76_timestamps = []
MCKO_timestamps = []

MKT_eventType = []
BV61_eventType = []
BV62_eventType = []
BV63_eventType = []
BV64_eventType = []
BV65_eventType = []
BV66_eventType = []
BV66A_eventType = []
KBSI_eventType = []
KBSO_eventType = []
BV69_eventType = []
BV70_eventType = []
BV70A_eventType = []
BV71_eventType = []
BV72_eventType = []
BV72A_eventType = []
FSDI_eventType = []
FSDO_eventType = []
BV74A_eventType = []
BV75_eventType = []
BV76_eventType = []
MCKO_eventType = []

for i, val in enumerate(body):
    if 'Event' in val:
        val_split = val.split()

        if val_split[0] == 'MKT_I':
            MKT_rowIDs.append(i)
            MKT_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            MKT_eventType.append(val_split[4])

        if val_split[0] == 'BV61_O':
            BV61_rowIDs.append(i)
            BV61_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV61_eventType.append(val_split[4])

        if val_split[0] == 'BV62_O':
            BV62_rowIDs.append(i)
            BV62_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV62_eventType.append(val_split[4])

        if val_split[0] == 'BV63_O':
            BV63_rowIDs.append(i)
            BV63_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV63_eventType.append(val_split[4])

        if val_split[0] == 'BV64_O':
            BV64_rowIDs.append(i)
            BV64_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV64_eventType.append(val_split[4])

        if val_split[0] == 'BV65_O':
            BV65_rowIDs.append(i)
            BV65_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV65_eventType.append(val_split[4])

        if val_split[0] == 'BV66_O':
            BV66_rowIDs.append(i)
            BV66_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV66_eventType.append(val_split[4])

        if val_split[0] == 'BV66A_O':
            BV66A_rowIDs.append(i)
            BV66A_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV66A_eventType.append(val_split[4])

        if val_split[0] == 'KBS_P1':
            KBSI_rowIDs.append(i)
            KBSI_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            KBSI_eventType.append(val_split[4])

        if val_split[0] == 'KBS_P2':
            KBSO_rowIDs.append(i)
            KBSO_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            KBSO_eventType.append(val_split[4])

        if val_split[0] == 'BV69_O':
            BV69_rowIDs.append(i)
            BV69_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV69_eventType.append(val_split[4])

        if val_split[0] == 'BV70_O':
            BV70_rowIDs.append(i)
            BV70_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV70_eventType.append(val_split[4])

        if val_split[0] == 'BV70A_O':
            BV70A_rowIDs.append(i)
            BV70A_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV70A_eventType.append(val_split[4])

        if val_split[0] == 'BV71_O':
            BV71_rowIDs.append(i)
            BV71_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV71_eventType.append(val_split[4])

        if val_split[0] == 'BV72_O':
            BV72_rowIDs.append(i)
            BV72_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV72_eventType.append(val_split[4])

        if val_split[0] == 'BV72A_O':
            BV72A_rowIDs.append(i)
            BV72A_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV72A_eventType.append(val_split[4])

        if val_split[0] == 'FSD_P1':
            FSDI_rowIDs.append(i)
            FSDI_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            FSDI_eventType.append(val_split[4])

        if val_split[0] == 'FSD_P2':
            FSDO_rowIDs.append(i)
            FSDO_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            FSDO_eventType.append(val_split[4])

        if val_split[0] == 'BV74A_O':
            BV74A_rowIDs.append(i)
            BV74A_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV74A_eventType.append(val_split[4])

        if val_split[0] == 'BV75_O':
            BV75_rowIDs.append(i)
            BV75_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV75_eventType.append(val_split[4])

        if val_split[0] == 'BV76_O':
            BV76_rowIDs.append(i)
            BV76_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            BV76_eventType.append(val_split[4])

        if val_split[0] == 'MCK_O':
            MCKO_rowIDs.append(i)
            MCKO_timestamps.append(datetime.strptime(val_split[1] + " " + val_split[2], '%d.%m.%Y %H:%M:%S.%f'))
            MCKO_eventType.append(val_split[4])


if station == 'MKT':
    for i, val in enumerate(MKT_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', MKT_rowIDs[i], '\tTimestamps:', val)
if station == 'BV61':
    for i, val in enumerate(BV61_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV61_rowIDs[i], '\tTimestamps:', val)
if station == 'BV62':
    for i, val in enumerate(BV62_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV62_rowIDs[i], '\tTimestamps:', val)
if station == 'BV63':
    for i, val in enumerate(BV63_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV63_rowIDs[i], '\tTimestamps:', val)
if station == 'BV64':
    for i, val in enumerate(BV64_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV64_rowIDs[i], '\tTimestamps:', val)
if station == 'BV65':
    for i, val in enumerate(BV65_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV65_rowIDs[i], '\tTimestamps:', val)
if station == 'BV66':
    for i, val in enumerate(BV66_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV66_rowIDs[i], '\tTimestamps:', val)
if station == 'BV66A':
    for i, val in enumerate(BV66A_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV66A_rowIDs[i], '\tTimestamps:', val)
if station == 'KBSI':
    for i, val in enumerate(KBSI_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', KBSI_rowIDs[i], '\tTimestamps:', val)
if station == 'KBSO':
    for i, val in enumerate(KBSO_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', KBSO_rowIDs[i], '\tTimestamps:', val)
if station == 'BV69':
    for i, val in enumerate(BV69_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV69_rowIDs[i], '\tTimestamps:', val)
if station == 'BV70':
    for i, val in enumerate(BV70_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV70_rowIDs[i], '\tTimestamps:', val)
if station == 'BV70A':
    for i, val in enumerate(BV70A_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV70A_rowIDs[i], '\tTimestamps:', val)
if station == 'BV71':
    for i, val in enumerate(BV71_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV71_rowIDs[i], '\tTimestamps:', val)
if station == 'BV72':
    for i, val in enumerate(BV72_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV72_rowIDs[i], '\tTimestamps:', val)
if station == 'BV72A':
    for i, val in enumerate(BV72A_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV72A_rowIDs[i], '\tTimestamps:', val)
if station == 'FSDI':
    for i, val in enumerate(FSDI_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', FSDI_rowIDs[i], '\tTimestamps:', val)
if station == 'FSDO':
    for i, val in enumerate(FSDO_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', FSDO_rowIDs[i], '\tTimestamps:', val)
if station == 'BV74A':
    for i, val in enumerate(BV74A_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV74A_rowIDs[i], '\tTimestamps:', val)
if station == 'BV75':
    for i, val in enumerate(BV75_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV75_rowIDs[i], '\tTimestamps:', val)
if station == 'BV76':
    for i, val in enumerate(BV76_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', BV76_rowIDs[i], '\tTimestamps:', val)
if station == 'MCK':
    for i, val in enumerate(MCKO_timestamps):
        print('Station:', station, '\tIndex:', i, '\tRow #:', MCKO_rowIDs[i], '\tTimestamps:', val)


buffer_timestamps = []
buffer_values = []
for i in range(start_row+1, start_row+501):
    val_split = body[i].split()
    if '---' in val_split[0]:
        break
    buffer_timestamps.append(datetime.strptime(val_split[0] + " " + val_split[1], '%d.%m.%Y %H:%M:%S.%f'))
    buffer_values.append(float(val_split[2])/1e5)

title = body[start_row][:-1] + ' with ' + str(len(buffer_values)) + ' values...'
plt.plot(buffer_timestamps, buffer_values, color='blue', label=title)
plt.legend()
plt.gcf().autofmt_xdate()
myFmt = mdates.DateFormatter('%H:%M:%S')
plt.gca().xaxis.set_major_formatter(myFmt)
plt.show()
