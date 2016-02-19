#!/usr/bin/python

import re
import datetime
import httplib2
import urllib
import argparse
import oauth2client
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from icalendar import Calendar

class ItgGcal :
    """Class to manage Google Calendar events"""
    
    LABEL_SUM_ITEA = 'Booking from ITEA calendar'

    def __init__(self, cred_secret_file, cred_validated_file, app_name) :
        
        self.cred_secret_file = cred_secret_file
        self.cred_validated_file = cred_validated_file
        self.app_name = app_name
        # Initiate connection
        self.cred = self.__get_cred()        
        self.service = discovery.build('calendar', 'v3', http=self.cred.authorize(httplib2.Http()))
    
    def __get_cred(self) :
        """Method to get Google Calendar credentials and create gcal validated file if needed"""

        store = oauth2client.file.Storage(self.cred_validated_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.cred_secret_file, 'https://www.googleapis.com/auth/calendar')
            flow.user_agent = self.app_name
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            credentials = tools.run_flow(flow, store, flags)
        return credentials
    
    def get_cal_id_from_url(self, gcal_private_url) :
        """Method to get Google ID of one calendar ID based on private URL"""
    
        match = re.search(r"ical\/(.*)\/private", gcal_private_url)
        if(match) :
            return match.group(1)
    
    def generate_event_for_itea(self, day, location) :
        """Method to generate Json value for ITEA event into one Google Calendar"""
    
        # Create event json
        startDate = datetime.datetime.strptime(day, "%Y%m%d")
        endDate = startDate + datetime.timedelta(days=1)
        event = {
          'summary': self.LABEL_SUM_ITEA,
          'location': location,
          'description': 'Booking with data from ITEA calendar - Powered by '+self.app_name,
          'start': {
            'date': str(startDate.strftime("%Y"))+'-'+str(startDate.strftime("%m"))+'-'+str(startDate.strftime("%d"))
          },
          'end': {
            'date': str(endDate.strftime("%Y"))+'-'+str(endDate.strftime("%m"))+'-'+str(endDate.strftime("%d"))
          },
        }
        # Return Json
        return event
    
    def insert_event(self, gcal_cal_id, event) :
        """Method to insert one event into one Google Calendar"""
        
        return self.service.events().insert(calendarId=gcal_cal_id,body=event).execute()   
    
    def del_event(self, gcal_cal_id, gcal_event_id) :
        """Method to delete one event of one Google Calendar"""
        
        self.service.events().delete(calendarId=gcal_cal_id, eventId=gcal_event_id).execute()
    
    def del_events_from_day(self, gcal_cal_id, day) :
        """Method to delete all one day events of one Google Calendar"""
        
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
        """Method to delete all events of one Google Calendar created from ITEA (search LABEL_SUM_ITEA)"""
        
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
    
    def export_from_ics_to_dic(self, url_ics) :
        """Method to export busy days of one Google Calendar to a dictionary : dic[ year ][ month ][ day ] = busy"""
        
        # Get data from ICS URL
        file = urllib.urlopen(url_ics)
        gcal = Calendar.from_ical(file.read())

        # Parsing of vevents
        tmpDic = {}
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
                    if str(currentDate.strftime("%Y")) not in tmpDic.keys() :
                        tmpDic[ str(currentDate.strftime("%Y")) ] = {}
                    if str(currentDate.strftime("%m")) not in tmpDic[ str(currentDate.strftime("%Y")) ].keys() :
                        tmpDic[ str(currentDate.strftime("%Y")) ][ str(currentDate.strftime("%m")) ] = {}
                    # Populate dictionnary
                    tmpDic[ str(currentDate.strftime("%Y")) ][ str(currentDate.strftime("%m")) ][ str(currentDate.strftime("%d")) ] = 'busy'
                    # Increment currentDate
                    currentDate += datetime.timedelta(days=1)
    
        # Close file and return dictionnary
        file.close()  
        return tmpDic