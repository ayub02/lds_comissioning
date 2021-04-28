import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


df = pd.read_csv('../data/pvalKBS.csv', header=0)

time = df['t_kbs'].to_list()
val = df['val_kbs_zero'].to_list()

f = interp1d(time, val)

time_new = np.arange(0, 118, 2/1000)
val_new = []

for t in time_new:
    val_new.append(f(t)/1.95)

df_new = pd.DataFrame(list(zip(time_new, val_new)), columns=['t', 'P'])

filename = 'pVal_BV66.csv'
path = '../output/'

if os.path.exists(path+filename):
    os.remove(path+filename)
    print('Removed ', filename)
else:
    df_new.to_csv(path+filename, index=False)
    print('File write successful \t\t', filename)

# plt.plot(time_new, val_new)
# plt.plot(time, val, '--')
# plt.show()



