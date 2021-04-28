import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from vcf_calc import VCFOperational_Pressure as VCF


def norm_density(_op_density, _pressure, _temp):
    return _op_density/VCF(_op_density, _pressure, _temp)


_data = pd.read_excel('E:\INTECH\Projects\PARCO MFM\Comissioning\Mass balance inquiry\data\oper_density.xlsx', header=0, sheet_name='Combined')

_timestamps = []
_timestamps_offset = []
MKT_norm_density_calc = []
KBS_norm_density_calc = []
for _index, _row in _data.iterrows():
    _timestamps.append(datetime.strptime(_row[0], '%m/%d/%y %H:%M'))
    _timestamps_offset.append(datetime.strptime(_row[0], '%m/%d/%y %H:%M') + timedelta(seconds=169860))
    MKT_norm_density_calc.append(norm_density(_row[3], _row[8], _row[7]))
    KBS_norm_density_calc.append(norm_density(_row[9], _row[14], _row[13]))

myFmt = mdates.DateFormatter('%d-%H:%M')
fig, ax = plt.subplots(1, 1)
fig.autofmt_xdate()

ax.plot(_timestamps_offset, _data['MKT_norm_density'].to_list(), label='MKT Norm Density from PSI')
ax.plot(_timestamps_offset, MKT_norm_density_calc, '--', label='MKT Norm Density from Temp of FT')

ax.plot(_timestamps, _data['KBS_norm_density'].to_list(), label='KBS Norm Density from PSI')
ax.plot(_timestamps, KBS_norm_density_calc, '--', label='KBS Norm Density from Temp of FT')
ax.xaxis.set_major_formatter(myFmt)
ax.legend()
plt.show()


