import sqlite3, struct
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib import pyplot as plt


conn = sqlite3.connect('.\PT_64.db')
cursor = conn.cursor()
fetchSql = """
SELECT * FROM raw_pt_values ORDER BY s_time ASC;
"""

cursor.execute(fetchSql)

times = []
values = []
while True:
    res = cursor.fetchone()
    if res == None:
        print("done with fetched rows")
        break
    # print(str(int(len(res[2])/8))+'d')
    valueList = struct.unpack(str(int(len(res[2])/8))+'d', res[2])
    values.extend(valueList)
    times.append(datetime.fromtimestamp(res[0]/1000))
    # print(res[0], res[1], valueList)

timediff = []
for i in range(len(times)-1):
    timediff.append((times[i+1]-times[i]).total_seconds())


ones = [1 for i in range(len(times))]
myFmt = mdates.DateFormatter('%d-%m-%Y  %H:%M:%S')
fig, ax = plt.subplots(2, 1)
fig.autofmt_xdate()
ax[0].plot(values)

ax[1].plot(times[1:], timediff)
ax[1].plot(times[1:], timediff, '.', markerfacecolor='green', markeredgecolor='green', markersize=2)
ax[1].xaxis.set_major_formatter(myFmt)
ax[1].set_ylim(24.975, 25.050)
print(len(values)/50)
print((times[-1]-times[0]).total_seconds())
plt.show()
