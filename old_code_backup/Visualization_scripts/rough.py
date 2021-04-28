import pandas as pd
from datetime import datetime

# current date and time
datetime_object = pd.Timestamp(datetime.strptime('2020-09-28 15:01:54.041', '%Y-%m-%d %H:%M:%S.%f'))
print(datetime_object)