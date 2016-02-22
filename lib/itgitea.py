#!/usr/bin/python

import re
import requests
from lxml import html

class ItgItea :
    """Class to manage ITEA Calendar events
        - self.first_year
        - self.first_month"""

    def _populate_dic_from_months(self, dic, months) :
        """Method to populate dictionnary from months list [{year1,month1},{year1,month2}]"""
  
        # Check
        if not isinstance(dic, dict) :
            raise TypeError('Param "dic" must be a dict')
        if not isinstance(months, list) :
            raise TypeError('Param "months" must be a list')
        # Init
        tmpDic = dic
        year = ''
        i = 0
        # Parsing of list
        for month in months :
            # Get start date
            if(i == 0) :
                self.first_year = int(month)
            if(i == 1) :
                self.first_month = int(month)
            # Build dictionnary
            if (i % 2) == 0 : # Year
                if(year != month) :
                    year = month
                    tmpDic[ str("%04d" % int(year)) ] = {}
            else : # Month
                tmpDic[ str("%04d" % int(year)) ][ str("%02d" % int(month)) ] = {}
            i += 1
        # Return dictionnary
        return tmpDic
    
    def _populate_dic_from_days(self, dic, days) :
        """Method to populate dictionnary from days list [{CssClassx,Daynumber1},{CssClassy,Daynumber2}]"""

        # Check
        if not isinstance(dic, dict) :
            raise TypeError('Param "dic" must be a dict')
        if not isinstance(days, list) :
            raise TypeError('Param "days" must be a list')
        # Init
        tmpDic = dic
        currentYear = self.first_year
        currentMonth = self.first_month
        currentDay = 1
        i = 0
        # Parsing of list  
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
                if day < currentDay :
                    if currentMonth == 12 :
                        currentYear = currentYear + 1
                        currentMonth = 1
                    else :
                        currentMonth = currentMonth + 1
                currentDay = day
                # Populate dictionnary
                tmpDic[ str("%04d" % int(currentYear)) ][ str("%02d" % int(currentMonth)) ][ str("%02d" % int(currentDay)) ] = dispo
            i += 1
        # Return dictionnary
        return tmpDic        
    
    def export_from_html_to_dic(self, url_html) :
        """Method to export ITEA Calendar to a dictionary : dic[ year ][ month ][ day ] = busy|nostatus|available"""

        # Get data from URL
        tree = html.fromstring(requests.get(url_html).content)
        class_room = "".join(tree.xpath('//option[@selected]/@data-classe_a_afficher'))
        months = tree.xpath('//caption[@data-annee]/@data-annee | //caption[@data-annee]/@data-mois')
        days = tree.xpath('//table[@class="calend"]//span[contains(@class,"'+class_room+'")]/@class | //table[@class="calend"]//span[contains(@class,"'+class_room+'")]/text()')
        
        tmpDic = {}
        # Parsing of months list and build structure [year][month]
        tmpDic = self._populate_dic_from_months(tmpDic,months)

        # Parsing of days list and fill structure [year][month][day] = busy|nostatus|available
        tmpDic = self._populate_dic_from_days(tmpDic,days)
    
        # Return dictionary
        return tmpDic