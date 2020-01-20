from __future__ import print_function
from datetime import datetime, timedelta, date
import pickle
import os.path
import calendar
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from re import search


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.today()
    max_time = now + timedelta(weeks=5)
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    max_time = datetime.strftime(max_time, '%Y-%m-%dT%H:%M:%S.000000Z')

    #Getting all events from now to the next 5 weeks
    print('\nGetting Out of office events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=2000, timeMax=max_time,  singleEvents=True,
                                          orderBy='startTime').execute()

    events = events_result.get('items', [])

    days = []
    startArray = []
    endArray = []

    #Check Out of Office events inside all events collected
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        #If event have tittle dont check
        if 'summary' in event:
            if search("Out of office", event['summary']):
                #Formating date for have a count of days
                start = start[:19]
                start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
                startArray.append(start)
                end = end[:19]
                end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
                days.append(end - start)
                end = end - timedelta(days=1)
                endArray.append(end)

    #Formating text of absence days
    i = 0
    if  len(startArray) != 0:
        print("Writting events out of office")
        signature = "<div name =\"Abscense_Start\"> <p style = 'font-weight: bold; margin-bottom: 0em; color:#E40046;'>Upcoming Absences:</p>"
        for start in startArray:
            if (days[i].days == 1):
                signature += ('<p style = "margin-top: 0.2em; margin-bottom: 0em; color:#E40046;">&nbsp;&nbsp;- ' + start.strftime("%d %B %Y") + '</p>')
            
            elif (days[i].days != 1 & start.month == endArray[i].month):
                signature += ('<p style = "margin-top: 0.2em; margin-bottom: 0em; color:#E40046;">&nbsp;&nbsp;- ' + start.strftime("%d") + ' to '  + endArray[i].strftime("%d %B %Y") + '</p>')
            
            elif (days[i].days != 1 & start.month != endArray[i].month):
                signature += ('<p style = "margin-top: 0.2em; margin-bottom: 0em; color:#E40046;">&nbsp;&nbsp;- ' + start.strftime("%d %B %Y") + ' to ' + endArray[i].strftime("%d %B %Y") +'</p>' )

            i+=1
        signature += "<div name =\"Abscense_Final\">"
    else:
        signature ="" 
        print("There is no events out of office")

    return signature
