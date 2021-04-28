from numpy import genfromtxt
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from itertools import cycle


def next_plot():
    return next(color_cycle)


color_cycle = cycle(['k',  'b', 'r',  'y', 'y',  'k', 'b',  'r'])
wave = (pd.read_csv('../data/pVal_BV66.csv', header=None)).to_numpy()

# NUM_SAMPLES_1_AVG = 500
NUM_SAMPLES_2_AVG = 150
START_SAMPLE_2_AVG = 10000
NPW_SAMPLE_BEFORE = 150
NPW_SAMPLE_AFTER = 350
NPW_THR = 0.1

NUM_SAMPLES_1_AVG_range = [15, 50, 200, 500]

plt.figure()
plt.plot(wave, '--', linewidth=1, color='b', label='Pressure values at BV66')
plt.axhline(y=NPW_THR, linewidth=0.5, color='r', label='Threshold: '+str(NPW_THR))
plt.ylim(0.085, 0.105)
plt.xlim(31850, 32150)
plt.ylabel('Pressure (bar)')
plt.xlabel('Number of samples')

for val in NUM_SAMPLES_1_AVG_range:

    NUM_SAMPLES_1_AVG = val
    queue = []
    NPW_THR_break = []
    diff = np.ones(wave.shape[0])*(-5)
    detected = False
    results = []
    queue_len = START_SAMPLE_2_AVG + NUM_SAMPLES_2_AVG

    for i in range(wave.shape[0]):
        val = wave[i][0]
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
    plt.plot(diff, color=_color, linewidth=0.5, label='NUM_SAMPLES_1_AVG: '+str(NUM_SAMPLES_1_AVG))

plt.legend()
plt.show()
