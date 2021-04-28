import numpy as np
from matplotlib import pyplot as plt

data = np.genfromtxt('NPW_actual_wave_long.csv', delimiter=',')

pts = data[:, 0]
PT_val = data[:, 1]

N1 = 3
N2 = 7
start_of_N2 = 5
num_before = 350
num_after = 150
threshold = 0.2*1000

buffer_len = max(num_before + num_after, start_of_N2+N2)

# a = np.arange(15)
# print(a)
# print(a[-N1:])
# print(a[-(N2+start_of_N2):-start_of_N2])

buffer = []
for val in PT_val:
    if len(buffer)<buffer_len:
        buffer.append(val)
    else:
        del buffer[0]
        buffer.append(val)
        buffer1 = buffer[-N1:]
        buffer2 = buffer[- (N2+start_of_N2): -start_of_N2]
        avg1 = sum(buffer1) / len(buffer1)
        avg2 = sum(buffer2) / len(buffer2)
        if abs(avg1-avg2) > threshold:







# plt.plot(pts, PT_val)
# plt.show()
