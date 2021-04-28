from numpy import genfromtxt
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from itertools import cycle


def next_plot():
    return next(color_cycle)


color_cycle = cycle(['k',  'b', 'r',  'y', 'y',  'k', 'b',  'r'])
df = pd.read_csv('../output/MQTT_KBS1_PT_3025__from__2020_12_10__00_50__to__2020_12_10__01_30____40msec.csv', header=0)
p_val = df['Values'].to_numpy()
p_avg = np.average(p_val)
wave = [val-p_val[0] for val in p_val]
wave = wave[:50000]


NUM_SAMPLES_1_AVG = 500
NUM_SAMPLES_2_AVG = 150
NPW_SAMPLE_BEFORE = 150
NPW_SAMPLE_AFTER = 350
NPW_THR = 0.05

START_SAMPLE_2_AVG_range = [10, 200]

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.plot(wave, '--', linewidth=1, color='b', label='Pressure values at BV66')
ax2.axhline(y=NPW_THR, linewidth=0.5, color='r', label='Threshold: '+str(NPW_THR))

for val in START_SAMPLE_2_AVG_range:

    START_SAMPLE_2_AVG = int(val/0.02)
    queue = []
    NPW_THR_break = []
    diff = np.ones(len(wave))*(-5)
    detected = False
    results = []
    queue_len = START_SAMPLE_2_AVG + NUM_SAMPLES_2_AVG

    for i in range(len(wave)):
        val = wave[i]
        if len(queue) >= queue_len:
            queue.pop(0)
        queue.append(val)

        if len(queue) == queue_len:
            avg1 = np.average(queue[-NUM_SAMPLES_1_AVG:])
            avg2 = np.average(queue[-(NUM_SAMPLES_2_AVG+START_SAMPLE_2_AVG):-START_SAMPLE_2_AVG])
            diff[i] = abs(avg1-avg2)
            if diff[i] < 0:
                diff[i] = 0
            if abs(avg1-avg2) >= NPW_THR and not detected:
                results.append(i)
                detected = True
                NPW_THR_break.append(i)
            if abs(avg1-avg2) < NPW_THR:
                detected = False

    _color = next_plot()
    a2, = ax2.plot(diff, color=_color, linewidth=0.5, label='START_SAMPLE_2_AVG: '+str(START_SAMPLE_2_AVG))

ax2.set_ylabel('Pressure (bar)')
ax1.set_xlabel('Number of points')
ax2.set_ylim(0, 0.7)
plt.legend()
plt.show()
