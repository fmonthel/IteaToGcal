#!/usr/bin/env python
#
# check-diff.py
#
# Simple wrapper that compare ITEA calendar to Google Agenda and fix
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#

import os
import ConfigParser
import argparse
import re
import datetime
from terminaltables import AsciiTable
from lib.itgmotor import ItgMotor
from lib.itggcal import ItgGcal
from lib.itgitea import ItgItea


# Parameters
time_start = datetime.datetime.now()
file_config = os.path.join(os.path.dirname(__file__), 'conf/config.ini')
Config = ConfigParser.ConfigParser()
Config.read(file_config)

# Options
parser = argparse.ArgumentParser(description='Report difference between ITEA and GCAL and propose to fix them')
parser.add_argument('--noauth_local_webserver', action='store_true', help='Needed for first execution (Google Agenda authentication)')
parser.add_argument('--action', action='store', dest='action', default='list-diff',
                    choices=['list-diff', 'create-google-events-from-itea', 'delete-google-events-from-itea'])
args = parser.parse_args()

# ITG objects instance
inst_itg = ItgMotor()
inst_itg_itea = ItgItea()
file_gcal = os.path.join(os.path.dirname(__file__), 'conf/gcal.json')
file_gcal_cred_validated = os.path.join(os.path.dirname(__file__), 'conf/gcal-credential-validated.json')
inst_itg_gcal = ItgGcal(file_gcal, file_gcal_cred_validated, Config.get('GLOBAL','application'))


# Parse ITEA calendar (REF) and populate dictionnary
dic_cal_itea = {}
for room, url in Config.items('ITEA_CALENDAR') :
    # Populate dic
    dic_cal_itea[ room ] = inst_itg_itea.export_from_html_to_dic(url)

# Parse Google agenda and populate dictionnary
dic_cal_gcal = {}
for room, url in Config.items('GOOGLE_CALENDAR') :
    # Populate dic
    dic_cal_gcal[ room ] = inst_itg_gcal.export_from_ics_to_dic(url)

# Get difference between calendar - dic_cal_itea is the reference
list_cal_diff = inst_itg.get_diff(dic_cal_itea,dic_cal_gcal)

# Ascii table
myAsciiTable = [['Room','Year','Month','Day','Message']]

# Parse list_cal_diff
for dic_item in list_cal_diff :
    # Build list for output
    tmpdata = list()
    tmpdata.append(dic_item['room'].upper()) # Room
    tmpdata.append(dic_item['year']) # Year
    tmpdata.append(dic_item['month']) # Month
    tmpdata.append(dic_item['day']) # Day
    # ITEA == YES but GCAL == NOT
    if dic_item['type'] == 'itea-yes-gcal-not' :
        # Create Google event ?
        if args.action == 'create-google-events-from-itea' :
            # Create event json
            endDate = datetime.datetime.strptime(dic_item['year']+dic_item['month']+dic_item['day'], "%Y%m%d")
            endDate += datetime.timedelta(days=1)
            event = {
              'summary': 'Booking from ITEA calendar',
              'location': Config.get('GLOBAL','location'),
              'description': 'Booking with data from ITEA calendar - Powered by '+Config.get('GLOBAL','application'),
              'start': {
                'date': dic_item['year']+'-'+dic_item['month']+'-'+dic_item['day']
              },
              'end': {
                'date': str(endDate.strftime("%Y"))+'-'+str(endDate.strftime("%m"))+'-'+str(endDate.strftime("%d"))
              },
            }
            # Id Gcal
            gcal_id = inst_itg_gcal.get_cal_id_from_url(Config.get('GOOGLE_CALENDAR',dic_item['room']))
            # Create event
            event_created = inst_itg_gcal.insert_event(gcal_id,event)
            # Add message to list
            tmpdata.append("Event created : "+event_created.get('htmlLink'))
        else :
            # Add message to list
            tmpdata.append("Itea calendar booked but Google agenda not")
    # ITEA == NOT but GCAL == YES
    if dic_item['type'] == 'itea-not-gcal-yes' :
        # Delete Google event ?
        if args.action == 'delete-google-events-from-itea' :
            # Id Gcal
            gcal_id = inst_itg_gcal.get_cal_id_from_url(Config.get('GOOGLE_CALENDAR',dic_item['room']))
            # Delete event
            events_deleted = inst_itg_gcal.del_events_from_day(gcal_id,dic_item['year']+dic_item['month']+dic_item['day'])
            # Report event correction
            mess_deleted = ''
            for event_deleted in events_deleted :
                if mess_deleted :
                    mess_deleted = mess_deleted+"\nEvent deleted : "+event_deleted.get('summary')
                else :
                    mess_deleted = "Event deleted : "+event_deleted.get('summary')
            if not mess_deleted :
                mess_deleted = "Google Agenda event already deleted"
            # Add message to list
            tmpdata.append(mess_deleted)
        else :
            # Add message to list
            tmpdata.append("Google Agenda booked but ITEA calendar not")
    
    # Add tmpdata list to myAsciiTable 
    myAsciiTable.append(tmpdata)
                    
# Create AsciiTable and total
tmpdata = list()
tmpdata.append("Total : " + str(len(myAsciiTable) - 1) + " row(s)")
tmpdata.append("")
tmpdata.append("")
tmpdata.append("")
tmpdata.append("")
myAsciiTable.append(tmpdata)
myTable = AsciiTable(myAsciiTable)
myTable.inner_footing_row_border = True
myTable.justify_columns[1] = myTable.justify_columns[2] = myTable.justify_columns[3] = 'right'

# End script
time_stop = datetime.datetime.now()
time_delta = time_stop - time_start

# Output data
print "######### Date : %s - App : %s #########" % (time_start.strftime("%Y-%m-%d"),Config.get('GLOBAL','application'))
print "- Start time : %s" % (time_start.strftime("%Y-%m-%d %H:%M:%S"))
print "- Finish time : %s" % (time_stop.strftime("%Y-%m-%d %H:%M:%S"))
print "- Delta time : %d second(s)" % (time_delta.total_seconds())
print myTable.table