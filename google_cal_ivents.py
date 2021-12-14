import pickle
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google_auth_oauthlib.helpers import credentials_from_session
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from datetime import datetime, timedelta


global caal_list, timeZone, calendar_id, current_cal
SCOPES = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes = SCOPES)
#credentials = flow.run_console()
#pickle.dump(credentials, open("token.pkl", "wb"))
credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)
def auth():
    return
def cal_list():
    
    caal_list = service.calendarList().list().execute()
    n = int(input("Enter number of calendars: ")) 
    for i in range(n):
        print(str(i), caal_list['items'][i]['summary'])

    current_cal = int(input("Choose the calendar you want: "))
    timeZone = caal_list['items'][current_cal]['timeZone']
    calendar_id = caal_list['items'][current_cal]['id']
    print(calendar_id, timeZone)
    start_time = datetime(2022, 1, 12, 19, 30, 0)
    end_time = start_time + timedelta(hours=1)
    timezone = timeZone
    summary = caal_list['items'][current_cal]['summary']


    event = {
      'summary': summary,
      'location': 'Hyderabad',
      'description': 'MI vs TBD',
      'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timezone,
      },
      'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timezone,
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()
    return
cal_list()


#result = service.calendarList().list().execute()
#print(result['items'])