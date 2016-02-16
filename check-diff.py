#!/usr/bin/env python
#
# check-diff.py
#
# Simple wrapper that compare ITEA calendar to Google Agenda and fix
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#

import ConfigParser
import argparse
import re
import datetime
from terminaltables import AsciiTable
from lib.itggcal import ItgGcal
from lib.itgitea import ItgItea


# Parameters
time_start = datetime.datetime.now()
Config = ConfigParser.ConfigParser()
Config.read('conf/config.ini')

# Options
parser = argparse.ArgumentParser(description='Report difference between ITEA and GCAL and propose to fix them')
parser.add_argument('--noauth_local_webserver', action='store_true', help='Needed for first execution (Google Agenda authentication)')
parser.add_argument('--action', action='store', dest='action', default='list-diff',
                    choices=['list-diff', 'create-google-events-from-itea', 'delete-google-events-from-itea'])
args = parser.parse_args()

# ITG Gcal and Itea instance
inst_itg_gcal = ItgGcal('conf/gcal.json', 'conf/gcal-credential-validated.json', Config.get('GLOBAL','application'))
inst_itg_itea = ItgItea()

# Parse Reference calendar (ITEA) and populate list
dRefCalendar = {}
for room, url in Config.items('ITEA_CALENDAR') :
    # Populate list
    dRefCalendar[ room ] = inst_itg_itea.export_itea_from_url_to_list(url)

# Parse Google agenda and populate list
dGcalCalendar = {}
for room, url in Config.items('GOOGLE_CALENDAR') :
    # Populate list
    dGcalCalendar[ room ] = inst_itg_gcal.export_gcal_from_ics_to_list(url)

# Ascii table
myAsciiTable = [['Room','Year','Month','Day','Message']]
# Check diff between dRefCalendar and dGcalCalendar
for room in sorted(dRefCalendar) :
    for year in sorted(dRefCalendar[ room ]) :
        for month in sorted(dRefCalendar[ room ][ year ]) :
            for day in sorted(dRefCalendar[ room ][ year ][ month ]) :
                # Get day value + build list
                rCal = dRefCalendar[ room ][ year ][ month ][ day ]
                tmpdata = list()
                tmpdata.append(room.upper()) # Room
                tmpdata.append(year) # Year
                tmpdata.append(month) # Month
                tmpdata.append(day) # Day
                # Process Google agenda
                if year not in dGcalCalendar[ room ].keys() :
                    gCal = 'available'
                elif month not in dGcalCalendar[ room ][ year ].keys() :
                    gCal = 'available'
                elif day not in dGcalCalendar[ room ][ year ][ month ].keys() :
                    gCal = 'available'
                else :
                    gCal = 'busy'
                # Compare values
                if rCal == gCal or rCal == 'nostatus' :
                    continue
                elif gCal == 'busy' :
                    # Google booked but not Itea
                    if args.action == 'delete-google-events-from-itea' :
                        # Id Gcal
                        gcal_id = inst_itg_gcal.get_gcal_id_from_url(Config.get('GOOGLE_CALENDAR',room))
                        # Create event
                        events_deleted = inst_itg_gcal.del_events_from_day(gcal_id,year+month+day)
                        # Report event correction
                        mess_deleted = ''
                        for event_deleted in events_deleted :
                            if mess_deleted :
                                mess_deleted = mess_deleted+"\nEvent deleted : "+event_deleted.get('summary')
                            else :
                                mess_deleted = "Event deleted : "+event_deleted.get('summary')
                        if not mess_deleted :
                            mess_deleted = "Google Agenda event already deleted"
                        tmpdata.append(mess_deleted)
                        myAsciiTable.append(tmpdata)
                    else :
                        tmpdata.append("Google Agenda booked but ITEA calendar not")
                        myAsciiTable.append(tmpdata)
                elif rCal == 'busy' :
                    # Create event json
                    endDate = datetime.datetime.strptime(year+month+day, "%Y%m%d")
                    endDate += datetime.timedelta(days=1)
                    event = {
                      'summary': 'Booking from ITEA calendar',
                      'location': Config.get('GLOBAL','location'),
                      'description': 'Booking with data from ITEA calendar - Powered by '+Config.get('GLOBAL','application'),
                      'start': {
                        'date': year+'-'+month+'-'+day
                      },
                      'end': {
                        #'date': year+'-'+month+'-'+day
                        'date': str(endDate.strftime("%Y"))+'-'+str(endDate.strftime("%m"))+'-'+str(endDate.strftime("%d"))
                      },
                    }
                    if args.action == 'create-google-events-from-itea' :
                        # Id Gcal
                        gcal_id = inst_itg_gcal.get_gcal_id_from_url(Config.get('GOOGLE_CALENDAR',room))
                        # Create event
                        event_created = inst_itg_gcal.insert_event(gcal_id,event)
                        # Report event correction
                        tmpdata.append("Event created : "+event_created.get('htmlLink')) # Fix
                        myAsciiTable.append(tmpdata)
                    else :
                        # Itea booked but not Google
                        tmpdata.append("Itea calendar booked but Google agenda not") # Issue
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