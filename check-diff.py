#!/usr/bin/env python
#
# check-diff.py
#
# Simple wrapper that compare ITEA calendar to Google Agenda
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#

import ConfigParser
import requests
import re
import urllib
import datetime
from lxml import html
from icalendar import Calendar
from terminaltables import AsciiTable

# Function to export ITEA data to list
def exportIteaToList(url_html) :

    # Get data from URL
    tree = html.fromstring(requests.get(url_html).content)
    months = tree.xpath('//caption[@data-annee]/@data-annee | //caption[@data-annee]/@data-mois')
    days = tree.xpath('//table[@class="calend"]//span[@style="display:block;"]/@class | //table[@class="calend"]//span[@style="display:block;"]/text()')

    # Parsing of date
    tmpList = {}
    year = ''
    i = 0
    for month in months :
        # Get start date
        if(i == 0) :
            firstYear = month
        if(i == 1) :
            firstMonth = month
        # Build list
        if (i % 2) == 0 : # Year
            if(year != month) :
                year = month
                tmpList[ str(year) ] = {}
        else : # Month
            tmpList[ str(year) ][ str("%02d" % int(month)) ] = {}
        i = i + 1

    # Parsing of days
    currentYear = int(firstYear)
    currentMonth = int(firstMonth)
    currentDay = 1
    i = 0
    for day in days :
        if (i % 2) == 0 : # Class
            classDay = day
            if(re.search(r"Cliquable", classDay)) :
                dispo = 'available'
            elif(re.search(r"occupe", classDay)) :
                dispo = 'busy'
            else :
                dispo = 'nostatus'
        else : # Day
            if(day < currentDay) :
                if(currentMonth == 12) :
                    currentYear = currentYear + 1
                    currentMonth =  1
                else :
                    currentMonth = currentMonth + 1
            currentDay = day
            tmpList[ str(currentYear) ][ str("%02d" % int(currentMonth)) ][ str("%02d" % int(currentDay)) ] = dispo
        i = i + 1
    
    # Return list
    return tmpList

# Function to export GCAL data to list
def exportGcalToList(file_ics) :
    
    # Get data from ICS file
    file = open(file_ics,'rb')
    gcal = Calendar.from_ical(file.read())

    # Parsing of vevents
    tmpList = {}
    for vevent in gcal.walk():
        if vevent.name == "VEVENT" and vevent.get('status') == "CONFIRMED":
            if re.search(r"^[0-9]{8}$", str(vevent.get('dtstart').to_ical())) and re.search(r"^[0-9]{8}$", str(vevent.get('dtend').to_ical())) :            
                startDate = datetime.datetime.strptime(vevent.get('dtstart').to_ical(), "%Y%m%d")
                endDate = datetime.datetime.strptime(vevent.get('dtend').to_ical(), "%Y%m%d")           
                currentDate = startDate
                while currentDate < endDate :
                    currentDate += datetime.timedelta(days=1)
                    if str(currentDate.year) not in tmpList.keys() :
                        tmpList[ str(currentDate.year) ] = {}
                    if str(currentDate.month) not in tmpList[ str(currentDate.year) ].keys() :
                        tmpList[ str(currentDate.year) ][ str(currentDate.month) ] = {}
                    tmpList[ str(currentDate.year) ][ str(currentDate.month) ][ str(currentDate.day) ] = 'busy'
    
    # Close file and return list
    file.close()
    return tmpList


# Parameters
Config = ConfigParser.ConfigParser()
Config.read('conf/config.ini')

# Parse Reference calendar (ITEA) and populate list
dRefCalendar = {}
for room, url in Config.items('ITEA_CALENDAR') :
    # Populate list
    dRefCalendar[ room ] = exportIteaToList(url)

# Parse Google agenda and populate list
dGcalCalendar = {}
for room, url in Config.items('GOOGLE_CALENDAR') :
    # Save file locally
    urllib.urlretrieve (url, "data/"+room+".ics")
    # Populate list
    dGcalCalendar[ room ] = exportGcalToList("data/"+room+".ics")

# Ascii table
myAsciiTable = [['Room','Year','Month','Day','Issue']]
# Check diff between dRefCalendar and dGcalCalendar
for room in dRefCalendar :
    for year in dRefCalendar[ room ] :
        for month in dRefCalendar[ room ][ year ] :
            for day in dRefCalendar[ room ][ year ][ month ] :
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
                # Compare value
                if rCal == gCal or rCal == 'nostatus' :
                    continue
                elif gCal == 'busy' :
                    # Google booked but not Itea
                    tmpdata.append("Google Agenda booked but ITEA calendar not") # Issue
                    myAsciiTable.append(tmpdata)
                elif rCal == 'busy' :
                    # Itea booked but not Google
                    tmpdata.append("Itea calendar booked but Google agenda not") # Issue
                    myAsciiTable.append(tmpdata)

# Create AsciiTable and total
tmpdata = list()
tmpdata.append("Total : " + str(len(myAsciiTable) - 1) + " issue(s)")
tmpdata.append("")
tmpdata.append("")
tmpdata.append("")
tmpdata.append("")
myAsciiTable.append(tmpdata)
myTable = AsciiTable(myAsciiTable)
myTable.inner_footing_row_border = True
myTable.justify_columns[1] = myTable.justify_columns[2] = myTable.justify_columns[3] = 'right'

# Output data
print myTable.table