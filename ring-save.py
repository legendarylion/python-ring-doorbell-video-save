# https://python-ring-doorbell.readthedocs.io/

# use command below to run
# PY ring-save.py

# NOTE: You may need to delete the cache file test_token.cache if it throws an error that the cache is expired
import os
import json
import getpass
import datetime
from datetime import timedelta
from pathlib import Path

from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

download_location = 'downloads/'
# NOTE: Customize download location
# G:\My Drive\_____PERSONAL\ring_recordings
download_location = 'G:/My Drive/_____PERSONAL/ring_recordings/'



# file path for the auth key
cache_file = Path(os.path.dirname(os.path.realpath(__file__)) + "\\test_token.cache")

# file path to store latest date to download up to (default to date of installation)
# requires format: %Y-%m-%d %H:%M:%S
date_file = Path(os.path.dirname(os.path.realpath(__file__)) + "\\date.cache")

# read the text of the date.cache file to set the date to start downloading from
last_download_date_time_str = date_file.read_text()

# OPTIONAL: override date to be the date you'd like to start downloading from
# last_download_date_time_str = '2021-05-24 00:00:00'

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

        # Get the recording event ID
        recording_id = event['id']

        # Get the time
        api_date_time_str = event['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        # Update the timestamp in the files to EST
        api_date_time_obj = datetime.datetime.strptime(api_date_time_str, '%Y-%m-%d %H:%M:%S') - timedelta(hours=4)

        # Create timestamp string
        time = api_date_time_obj.strftime('%Y-%m-%d %H-%M-%S')

        # Create file name out of time, set filetype
        name = time + '.mp4'

        # optionally print to screen
        print('--' * 50)
        print('INC:      %s' % incrementor)
        print('ID:       %s' % event['id'])
        # print('Kind:     %s' % event['kind'])
        # print('Answered: %s' % event['answered'])
        print('TIME:     %s' % time)

        incrementor += 1

        if api_date_time_obj > last_download_time_obj:
            try:
                doorbell.recording_download(recording_id, filename=download_location+'%s' % name, override=True, timeout=120)
                date_file.write_text(api_date_time_obj.strftime("%Y-%m-%d %H:%M:%S"))
                print('STATUS:     Downloaded')
            except:
                print('STATUS:     Failed!')
        else:
            print('File already saved, skipping...')

    # End Script Message    
    print('--' * 50)
    print('')
    print('Script Completed!')
    print('')
    print('--' * 50)
    print('')
    print('')

if __name__ == "__main__":
    main()
