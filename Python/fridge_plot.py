from dateutil import parser
import datetime
import pandas as pd
import json
from matplotlib.dates import DateFormatter

def fridge_plot(directory, variable, start_date, end_date = None):
    begin = parser.parse(start_date)
    if end_date is None:
        end = begin
    else:
        end = parser.parse(end_date)
    delta = end - begin
    date_list =  []
    for i in range(delta.days + 2):
        date_list.append((begin + datetime.timedelta(days = i)).date().strftime('%Y%m%d'))
    date_set = set(date_list)
    data_dict = []
    for date in date_set:
        try:
            with open(directory + 'triton_' + date, 'r') as f:
                for line in f:
                    data_dict.append(json.loads(line[:-2]))
        except IOError:
            pass
    df = pd.DataFrame.from_dict(data_dict)
    if len(data_dict) == 0:
        print("Error: No data")
        return df
    df['time']=pd.to_datetime(df['time'])
    df = df[(pd.to_datetime(begin) <= df['time']) & (df['time'] <= pd.to_datetime(end))]
    ax=df.plot(x='time',y=variable)
    ax.xaxis.set_major_formatter(DateFormatter('%m-%d %I:%M:%S %p'))
    return df
