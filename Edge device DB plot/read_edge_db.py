import os
import struct
import sqlite3
import numpy as np
import configparser
import pandas as pd
import tkinter as tk
from tkinter import *
from tkcalendar import *
from functools import partial
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from datetime import datetime, timedelta


class DB:
    def __init__(self, _root):
        self.root = []
        self.timestamps = []
        self.pVals = []
        self.sample_rates = []
        self.NUM_SAMPLES_1_AVG = 0
        self.NUM_SAMPLES_2_AVG = 0
        self.START_SAMPLE_2_AVG = 0
        self.NPW_SAMPLE_BEFORE = 0
        self.NPW_SAMPLE_AFTER = 0
        self.NPW_THR = 0
        self._from_date = datetime.now()
        self._to_date = datetime.now()
        self.start_timestamp = datetime.now()
        self.end_timestamp = datetime.now()
        self.read_settings()

        now = datetime.now()
        hours = [val for val in range(0, 25)]
        minutes = [val for val in range(0, 60, 5)]
        self.banner_text = StringVar()
        self.from_hour = IntVar()
        self.from_min = IntVar()
        self.to_hour = IntVar()
        self.to_min = IntVar()
        self.from_hour.set(0)
        self.from_min.set(0)
        self.to_hour.set(0)
        self.to_min.set(0)
        self.entry_widget = tk.Entry(self.root, width=70)
        self.entry_widget.grid(row=0, column=1)
        self.browse_button = tk.Button(self.root, text="Browse", command=self.func_browse).grid(row=0, column=2)
        self.analyze_button = tk.Button(self.root, text="Analyze", command=self.read_DB_file).grid(row=0, column=4)

    def read_settings(self):
        # Reading NPW settings
        settings = configparser.ConfigParser()
        settings.read('../config/NPW.ini')
        self.NUM_SAMPLES_1_AVG = int(settings['Edge_settings']['NUM_SAMPLES_1_AVG'])
        self.NUM_SAMPLES_2_AVG = int(settings['Edge_settings']['NUM_SAMPLES_2_AVG'])
        self.START_SAMPLE_2_AVG = int(settings['Edge_settings']['START_SAMPLE_2_AVG'])
        self.NPW_SAMPLE_BEFORE = int(settings['Edge_settings']['NPW_SAMPLE_BEFORE'])
        self.NPW_SAMPLE_AFTER = int(settings['Edge_settings']['NPW_SAMPLE_AFTER'])
        self.NPW_THR = float(settings['Edge_settings']['NPW_THR'])

    def read_DB_file(self):
        _db_path = self.entry_widget.get()
        # Reading DB file
        print('Reading database file ...')
        try:
            assert os.path.exists(_db_path) is True
        except:
            raise ValueError('File does not exist at specified path {}'.format(_db_path))
        conn = sqlite3.connect(_db_path)
        cursor = conn.cursor()
        fetchSql = """
        SELECT * FROM raw_pt_values ORDER BY s_time ASC;
        """
        cursor.execute(fetchSql)
        print('File read successfully')
        print('Unpacking buffers in file ...')
        _timestamps = []
        _sample_rates = []
        _pVals = []
        print('Reading rows in file ...')
        while True:
            res = cursor.fetchone()
            if not res:
                print("Done with reading file rows")
                break
            valueList = struct.unpack(str(int(len(res[2]) / 8)) + 'd', res[2])
            _sample_rates.extend([res[1]] * len(valueList))
            _pVals.extend([round(val, 3) for val in valueList])
            _timestamps.extend(self.gen_timestamps(res[0], len(valueList), res[1]))
            assert len(_sample_rates) == len(_pVals)
            assert len(_timestamps) == len(_pVals)

        self.timestamps = _timestamps
        self.pVals = _pVals
        self.sample_rates = _sample_rates
        self.gen_buffers()

    def func_browse(self):
        self.entry_widget.delete(0, END)
        self.entry_widget.insert(tk.END, tk.filedialog.askopenfilename(filetypes=(("DB files", "*.db"),)))

    @staticmethod
    def gen_timestamps(_start, _len, _sampling_rate):
        _timestamps = [datetime.fromtimestamp(_val) for _val in np.arange(_start / 1000,
                                                                          _start / 1000 + _sampling_rate / 1000 * _len,
                                                                          _sampling_rate / 1000)][:_len]
        return _timestamps

    def gen_buffers(self):
        _Buffer = []
        _Buffer_end = []
        _Buffer_start = []
        _NPW_THR_break = []
        _threshold_break_index = []
        _detected = np.zeros(len(self.pVals), dtype=bool)
        detected = False
        _results = []
        counter = 0
        print('Start:', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f'))
        _start_i = self.NUM_SAMPLES_1_AVG + self.START_SAMPLE_2_AVG + self.NUM_SAMPLES_2_AVG
        sum1_i = self.NUM_SAMPLES_1_AVG + self.START_SAMPLE_2_AVG + self.NUM_SAMPLES_2_AVG
        sum2_i = self.NUM_SAMPLES_2_AVG
        sum1 = sum(self.pVals[sum1_i - self.NUM_SAMPLES_1_AVG:sum1_i])
        sum2 = sum(self.pVals[sum2_i - self.NUM_SAMPLES_2_AVG:sum2_i])
        diff = [self.NPW_THR * 2] * (sum1_i - 1)
        diff.append(sum1 / self.NUM_SAMPLES_1_AVG - sum2 / self.NUM_SAMPLES_2_AVG)
        for i in range(_start_i, len(self.pVals)):
            sum1 = sum1 - self.pVals[i - self.NUM_SAMPLES_1_AVG] + self.pVals[i]
            sum2 = sum2 - self.pVals[i - self.NUM_SAMPLES_1_AVG - self.START_SAMPLE_2_AVG - self.NUM_SAMPLES_2_AVG] + self.pVals[i - self.NUM_SAMPLES_1_AVG - self.START_SAMPLE_2_AVG]
            diff.append(sum1 / self.NUM_SAMPLES_1_AVG - sum2 / self.NUM_SAMPLES_2_AVG)

        for i in range(len(self.pVals)):
            _detected[i] = detected
            if diff[i] < self.NPW_THR and not detected and counter == 0:
                _results.append(i)
                detected = True
                _NPW_THR_break.append(self.timestamps[i])
                _Buffer_start.append(
                    self.timestamps[i] + timedelta(seconds=-self.NPW_SAMPLE_BEFORE * self.sample_rates[i] / 1000))
                _Buffer_end.append(
                    self.timestamps[i] + timedelta(seconds=self.NPW_SAMPLE_AFTER * self.sample_rates[i] / 1000))
                _Buffer.append(self.pVals[i - self.NPW_SAMPLE_BEFORE:i + self.NPW_SAMPLE_AFTER])
                counter = self.NPW_SAMPLE_AFTER + self.NPW_SAMPLE_BEFORE
                print('Buffer start TS: ', _Buffer_start[-1].strftime('%Y-%m-%d %H:%M:%S.%f'))
            if counter > 0:
                counter -= 1
            if diff[i] > self.NPW_THR:
                detected = False
        assert len(diff) == len(self.timestamps)
        print('End:', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f'))

        myFmt = mdates.DateFormatter('%d-%m-%Y  %H:%M:%S')
        fig, ax = plt.subplots(2, 1)
        fig.autofmt_xdate()

        spacing = int(np.floor(len(self.timestamps)/1e5))
        print('Start', datetime.now())
        print('Plotting every {}th value'.format(spacing))
        ax[0].plot(self.timestamps[::spacing], self.pVals[::spacing])
        ax[0].xaxis.set_major_formatter(myFmt)
        for val in _Buffer_start:
            ax[1].axvline(x=val, linestyle='--', color='k')
        ax[1].plot(self.timestamps[::100], diff[::100], label='Diff of avg')
        ax[1].axhline(y=self.NPW_THR, label='NPW threshold', color='r')
        ax[1].xaxis.set_major_formatter(myFmt)
        ax[1].set_ylim(-1.5*abs(self.NPW_THR), 1.5*abs(self.NPW_THR))
        ax[1].legend()
        plt.show()
        print('End', datetime.now())


root = tk.Tk()
db = DB(root)

root.mainloop()
