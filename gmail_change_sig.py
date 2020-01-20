from __future__ import print_function

from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import my_calendar

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly']

store = file.Storage('storage.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

addresses = GMAIL.users().settings().sendAs().list(userId='me',
        fields='sendAs(isPrimary,sendAsEmail)').execute().get('sendAs')
for address in addresses:
    if address.get('isPrimary'):
        break
    
#Getting actual signature
rsp = GMAIL.users().settings().sendAs().patch(userId='me',
        sendAsEmail=address['sendAsEmail']).execute()

#Getting if exist absences days 
abscenses = my_calendar.main()
actual_sig = rsp['signature']

#If there is any absence days in the actual signature we gonna deleted that text and remplace for the new abscense days text
if "Upcoming Absences:" in actual_sig:
        firstDelPos=actual_sig.find("<div name=\"Abscense_Start\">") 
        secondDelPos=actual_sig.find("<div name=\"Abscense_Final\">") 
        actual_sig = actual_sig.replace(actual_sig[firstDelPos:secondDelPos+10+17], "")
        print("Deleting current abscences")

#Remplace the final result of the signature text
DATA = {'signature' : abscenses + actual_sig}  
rsp = GMAIL.users().settings().sendAs().patch(userId='me',
        sendAsEmail=address['sendAsEmail'], body=DATA).execute()

print("Days out of office signature script finalized")
