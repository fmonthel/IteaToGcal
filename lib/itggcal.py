#!/usr/bin/python

import re
import datetime
import httplib2
import urllib
import oauth2client
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from icalendar import Calendar

class ItgGcal :
    
    LABEL_SUM_ITEA = 'Booking from ITEA calendar'

    def __init__(self, cred_secret_file, cred_validated_file, app_name) :
        
        self.cred_secret_file = cred_secret_file
        self.cred_validated_file = cred_validated_file
        self.app_name = app_name
        # Initiate connection
        self.cred = self._get_cred()        
        self.service = discovery.build('calendar', 'v3', http=self.cred.authorize(httplib2.Http()))
    
    def _get_cred(self) :

        credentials = oauth2client.file.Storage(self.cred_validated_file).get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.cred_secret_file, 'https://www.googleapis.com/auth/calendar')
            flow.user_agent = self.app_name
            credentials = tools.run(flow, store)
        return credentials
    
    def get_gcal_id_from_url(self, gcal_private_url) :
    
        match = re.search(r"ical\/(.*)\/private", gcal_private_url)
        if(match) :
            return match.group(1)
    
    def insert_event(self, gcal_cal_id, event) :
        
        return self.service.events().insert(calendarId=gcal_cal_id,body=event).execute()   
    
    def del_event(self, gcal_cal_id, gcal_event_id) :
        
        self.service.events().delete(calendarId=gcal_cal_id, eventId=gcal_event_id).execute()
    
    def del_events_from_day(self, gcal_cal_id, day) :
        
        # Init data
        day = datetime.datetime.strptime(day, "%Y%m%d")
        page_token = None
        tmpList = []
       # Loop
        while True :
            events = self.service.events().list(calendarId=gcal_cal_id, timeMin=day.strftime("%Y-%m-%dT00:00:00Z"),
                                                timeMax=day.strftime("%Y-%m-%dT23:00:00Z"), pageToken=page_token).execute()
            for event in events['items'] :
                # Keep data for reporting
                tmpList.append(event)
                # Delete event
                self.del_event(gcal_cal_id, event['id'])
            page_token = events.get('nextPageToken')
            if not page_token :
                break
        # Return list
        return tmpList
    
    def del_events_created_from_itea(self, gcal_cal_id) :
        
        # Init data
        page_token = None
        tmpList = []
        # Loop
        while True :
            events = self.service.events().list(calendarId=gcal_cal_id, q=self.LABEL_SUM_ITEA, pageToken=page_token).execute()
            for event in events['items'] :
                # Keep data for reporting
                tmpList.append(event)
                # Delete event
                self.del_event(gcal_cal_id, event['id'])
            page_token = events.get('nextPageToken')
            if not page_token :
                break
        # Return list
        return tmpList
    
    def export_gcal_from_ics_to_list(self, url_ics) :
        
        # Get data from ICS URL
        file = urllib.urlopen(url_ics)
        gcal = Calendar.from_ical(file.read())

        # Parsing of vevents
        tmpList = {}
        for vevent in gcal.walk() :
            if vevent.name == "VEVENT" and vevent.get('status') == "CONFIRMED" :
                startDate = str(vevent.get('dtstart').to_ical())[:8]
                startDate = datetime.datetime.strptime(startDate, "%Y%m%d")
                if vevent.get('dtend') is None or vevent.get('dtstart') == vevent.get('dtend') :
                    endDate = str(vevent.get('dtstart').to_ical())[:8]
                    endDate = datetime.datetime.strptime(endDate, "%Y%m%d")
                    endDate += datetime.timedelta(days=1)
                else :
                    endDate = str(vevent.get('dtend').to_ical())[:8]
                    endDate = datetime.datetime.strptime(endDate, "%Y%m%d")
                currentDate = startDate
                while currentDate < endDate :
                    if str(currentDate.strftime("%Y")) not in tmpList.keys() :
                        tmpList[ str(currentDate.strftime("%Y")) ] = {}
                    if str(currentDate.strftime("%m")) not in tmpList[ str(currentDate.strftime("%Y")) ].keys() :
                        tmpList[ str(currentDate.strftime("%Y")) ][ str(currentDate.strftime("%m")) ] = {}
                    tmpList[ str(currentDate.strftime("%Y")) ][ str(currentDate.strftime("%m")) ][ str(currentDate.strftime("%d")) ] = 'busy'
                    # Increment currentDate
                    currentDate += datetime.timedelta(days=1)
    
        # Close file and return list
        file.close()  
        return tmpList