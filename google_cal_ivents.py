import pickle
import os
import datetime
#import main_parser
#from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google_auth_oauthlib.helpers import credentials_from_session
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import json
caal_list, calendar_id, timeZone, current_cal,datetime1,summary,description,location,start_time1 = 0,0,0,0,0,0,0,0,0

SCOPES = ['https://www.googleapis.com/auth/calendar']
flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes = SCOPES)
#credentials = flow.run_console()
#pickle.dump(credentials, open("token.pkl", "wb"))
credentials = pickle.load(open("token.pkl", "rb"))
service = build("calendar", "v3", credentials=credentials)
def auth():





    return

def cal_list():
    global caal_list, calendar_id, timeZone, current_cal
    caal_list = service.calendarList().list().execute()
    print(len(caal_list['items']))
    n = len(caal_list['items'])
    for i in range(n):
        print(str(i), caal_list['items'][i]['summary'])

    current_cal = int(input("Choose the calendar you want: "))
    timeZone = caal_list['items'][current_cal]['timeZone']
    calendar_id = caal_list['items'][current_cal]['id']
    print(calendar_id, timeZone)
    return caal_list, calendar_id, timeZone, current_cal

def parser():
    #with open('file.txt', 'r') as fr:
        #timetable = json.load(fr)
    global summary, location, description, datetime1,start_time1
    timetable = main_parser.get_all_timetable()
    week = int(input("choose getting week: "))
    event = []
    number_of_days = len(timetable[week-1][3])
    for i in range(number_of_days):
        datetime1 = [0,0,0,0,0,0]
        date_1 = timetable[week-1][3][i][1]
        datetime1[0] = str(date_1[date_1.rfind('.')+1:date_1.rfind('.')+5]) #year
        datetime1[1] = str(date_1[date_1.find('.')+1:date_1.rfind('.')])  #month
        datetime1[2] = str(date_1[0:date_1.find('.')]) #day
        number_of_lessons = len(timetable[week-1][3][i][2])
        for e in range(number_of_lessons):
            location = str(timetable[week-1][3][i][2][e][3])
            description = timetable[week-1][3][i][2][e][4]
            summary = timetable[week-1][3][i][2][e][1:3]
            y = timetable[week-1][3][i][2][e][0]
            if y.find('(') != -1:
                datetime1[3] = str(y[y.find('(')+1:y.find(':')]) #hour
                datetime1[4] = str(y[y.find(':')+1:y.find(':')+3]) #minute
            else:
                datetime1[3]= str(y[0:y.find('.')]) #hour
                datetime1[4]= str(y[y.find('.')+1:y.find('.')+3]) #minute
            #start_time1 = ' '.join([str(i) for i in datetime1])
            start_time1= datetime1
            print(start_time1)  
            print(e+1,summary,description,location, 'done')
            create_event()
    print(" ")
        
    #print("Number of days in the list: ", number_of_days)
    return

def create_event():
    start_time = datetime(int(start_time1[0]),int(start_time1[1]),int(start_time1[2]),int(start_time1[3]),int(start_time1[4]),int(start_time1[5]))
    end_time = start_time + timedelta(hours=1)


    event = {
      'summary': summary,
      'location': location,
      'description': description,
      'start': {
        'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timeZone,
      },
      'end': {
        'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': timeZone,
      },
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }
    service.events().insert(calendarId=calendar_id, body=event).execute()
    return

cal_list()
parser()
#create_event()

#print(calendar_id, timeZone, current_cal, summary,description,location)
#result = service.calendarList().list().execute()
#print(result['items'])