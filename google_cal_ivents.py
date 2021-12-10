import pickle
import os
import datetime
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from Google import Create_Service


CLIENT_SECRET_FILE = 'client_secret_915218010288-q43peel5culm6l2f7ujogd62gc75e104.apps.googleusercontent.com.json'
SCOPES = ['https://www.googleapis.com/calendar']
API_NAME = 'LK_PARSER'
API_VERSION = 'V3'

service = Create_Service(CLIENT_SECRET_FILE, SCOPES, API_NAME, API_VERSION)
    
calendar_list_entry = service.calendarList().get(calendarId='calendarId').execute()
    print(calendar_list_entry['summary'])