#!/usr/bin/python

import re
import requests
from lxml import html

class ItgItea :
    """Class to manage ITEA Calendar events"""

    def export_itea_from_url_to_dic(self, url_html) :
        """Method to export ITEA Calendar to a dictionary : dic[ year ][ month ][ day ] = busy|nostatus|available"""

        # Get data from URL
        tree = html.fromstring(requests.get(url_html).content)
        class_room = "".join(tree.xpath('//option[@selected]/@data-classe_a_afficher'))
        months = tree.xpath('//caption[@data-annee]/@data-annee | //caption[@data-annee]/@data-mois')
        days = tree.xpath('//table[@class="calend"]//span[contains(@class,"'+class_room+'")]/@class | //table[@class="calend"]//span[contains(@class,"'+class_room+'")]/text()')

        # Parsing of date
        tmpDic = {}
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
                    tmpDic[ str("%04d" % int(year)) ] = {}
            else : # Month
                tmpDic[ str("%04d" % int(year)) ][ str("%02d" % int(month)) ] = {}
            i = i + 1

        # Parsing of days
        currentYear = int(firstYear)
        currentMonth = int(firstMonth)
        currentDay = 1
        i = 0
        for day in days :
            if (i % 2) == 0 : # Class
                classDay = day
                if re.search(r"Cliquable", classDay) :
                    dispo = 'available'
                elif re.search(r"occupe", classDay) :
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
                tmpDic[ str("%04d" % int(currentYear)) ][ str("%02d" % int(currentMonth)) ][ str("%02d" % int(currentDay)) ] = dispo
            i = i + 1
    
        # Return dictionary
        return tmpDic