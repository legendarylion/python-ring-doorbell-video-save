import datetime

last_download_date_time_str = '2021-02-21 08:15:27'
last_download_time_obj = datetime.datetime.strptime(last_download_date_time_str, '%Y-%m-%d %H:%M:%S')

api_date_time_str = '2021-03-01 14:58:26'
api_date_time_obj = datetime.datetime.strptime(api_date_time_str, '%Y-%m-%d %H:%M:%S')

if api_date_time_obj < last_download_time_obj:
    print(api_date_time_obj)

else:
    print(last_download_time_obj)