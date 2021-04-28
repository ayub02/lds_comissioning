import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


# std dev = 0.014392293

path = '../output/'
from_file = 'MQTT_BV64_PT_64__from__2020_12_18__17_41__to__2020_12_18__18_11'

do_plot = True
do_export = True

df = pd.read_csv(path+from_file+'.csv', header=0)

time = df['Seconds'].to_list()
val = df['Values'].to_list()

sampling_rate = 20              # msec

f = interp1d(time, val, kind='linear')
assert time[0] == 0
assert time[-1] > time[0]

time_new = np.arange(0, int(np.floor(time[-1])), sampling_rate/1000)
val_new = []

for t in time_new:
    val_new.append(f(t))

if do_plot:
    plt.plot(time_new, val_new)
    plt.plot(time, val, '--')
    plt.show()

if do_export:
    to_file = from_file+'____'+str(sampling_rate)+'msec'

    df_new = pd.DataFrame(list(zip(time_new, val_new)), columns=['Seconds', 'Values'])
    if os.path.exists(path+to_file+'.csv'):
        os.remove(path+to_file+'.csv')
        print('Removed ', to_file+'.csv')
    else:
        df_new.to_csv(path+to_file+'.csv', index=False)
        print('File write successful \t\t', to_file+'.csv')

