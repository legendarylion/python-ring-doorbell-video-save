# https://python-ring-doorbell.readthedocs.io/
# to run
# PY test.py
# NOTE: You may need to delete the cache file test_token.cache if it throws an error that the cache is expired

import json
import getpass
import datetime
from pathlib import Path

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError


cache_file = Path("test_token.cache")


# Customize date to be the date you'd like to start downloading from
last_download_date_time_str = '2021-03-01 00:00:00'

last_download_time_obj = datetime.datetime.strptime(last_download_date_time_str, '%Y-%m-%d %H:%M:%S')

def token_updated(token):
    cache_file.write_text(json.dumps(token))


def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code


def main():
    if cache_file.is_file():
        auth = Auth("MyProject/1.0", json.loads(cache_file.read_text()), token_updated)
    else:
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        auth = Auth("MyProject/1.0", None, token_updated)
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            auth.fetch_token(username, password, otp_callback())

    ring = Ring(auth)
    ring.update_data()

    devices = ring.devices()
    # print(devices)

    doorbells = devices["doorbots"]
    chimes = devices["chimes"]
    stickup_cams = devices["stickup_cams"]

    # define doorbell
    doorbell = devices['doorbots'][0]

    # set event type
    events = doorbell.history(kind='motion', limit=1500)
    # reverse events to be in chronological order
    chronological_event_list = events[::-1]

    incrementor = 0

    for event in chronological_event_list:
        print('ID:       %s' % event['id'])
        # print('Kind:     %s' % event['kind'])
        # print('Answered: %s' % event['answered'])
        # print('When:     %s' % event['created_at'])
        print('--' * 50)

        recording_id = event['id']
        time = event['created_at'].strftime('%Y-%m-%d %H-%M-%S')
        name = time + '.mp4'

        api_date_time_str = event['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        api_date_time_obj = datetime.datetime.strptime(api_date_time_str, '%Y-%m-%d %H:%M:%S')

        incrementor += 1

        print('INC:      %s' % incrementor)

        if api_date_time_obj > last_download_time_obj:
            try:
                doorbell.recording_download(recording_id, filename='%s' % name, override=True, timeout=120)
                print(api_date_time_obj)
            except:
                print('failed')



if __name__ == "__main__":
    main()
