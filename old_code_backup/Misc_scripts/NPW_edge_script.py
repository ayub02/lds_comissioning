from numpy import genfromtxt
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


NUM_SAMPLES_1_AVG = 500
NUM_SAMPLES_2_AVG = 150
START_SAMPLE_2_AVG = int(200/0.02)
NPW_SAMPLE_BEFORE = 150
NPW_SAMPLE_AFTER = 350
NPW_THR = 0.1

wave = (pd.read_csv('../data/pVal_BV66.csv', header=None)).to_numpy()

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
        if diff[i]<0:
            diff[i] = 0
        if abs(avg1-avg2) >= NPW_THR and not detected:
            results.append(i)
            detected = True
            NPW_THR_break.append(i)
        if abs(avg1-avg2) < NPW_THR:
            detected = False


fig, ax1 = plt.subplots()
plt.ylim(-0.2, 0.15)
plt.ylabel('Pressure (bar)')

ax1.plot(wave, '--', linewidth=0.5, color='y', label='Pressure values at BV66')
ax1.plot(diff, color='c', linewidth=0.5, label='Difference of averages')
ax1.axhline(y=NPW_THR, linewidth=0.5, color='r', label='Threshold: '+str(NPW_THR))

# for val in NPW_THR_break:
#     ax1.axvline(val, linewidth=0.5, color='g', label='Location of threshold breach')

# print('Threshold breach indexes:', results, '\n')

for i in range(1, len(results)):
    if results[i] < results[i-1]+500:
        results[i] = results[i - 1] + 500
print(results)
if results:
    for val in results:
        print([round(value[0], 3) for value in list(wave[val-NPW_SAMPLE_BEFORE:val+NPW_SAMPLE_AFTER])])
        x = np.arange(val - NPW_SAMPLE_BEFORE, val + NPW_SAMPLE_AFTER)
        ax1.plot(x, [round(value[0], 3) for value in list(wave[val - NPW_SAMPLE_BEFORE:val + NPW_SAMPLE_AFTER])],
                 label='NPW buffer generated')

ax1.text(0, -0.14, 'NUM_SAMPLES_1_AVG: ' + str(NUM_SAMPLES_1_AVG), fontsize=8)
ax1.text(0, -0.16, 'NUM_SAMPLES_2_AVG: ' + str(NUM_SAMPLES_2_AVG), fontsize=8)
ax1.text(0, -0.18, 'START_SAMPLE_2_AVG: ' + str(START_SAMPLE_2_AVG), fontsize=8)


ax1.legend()
plt.show()
