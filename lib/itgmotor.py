#!/usr/bin/python

class ItgMotor :
        
    def get_diff(self,dic_itea,dic_gcal) :
        
        # Init
        tmpList = list()
        # Parse ITEA dic = the reference
        for room in sorted(dic_itea) :
            for year in sorted(dic_itea[ room ]) :
                for month in sorted(dic_itea[ room ][ year ]) :
                    for day in sorted(dic_itea[ room ][ year ][ month ]) :
                        # Get Itea day value
                        day_value_itea = dic_itea[ room ][ year ][ month ][ day ]
                        # Get Google day value
                        if year not in dic_gcal[ room ].keys() :
                            day_value_gcal = 'available'
                        elif month not in dic_gcal[ room ][ year ].keys() :
                            day_value_gcal = 'available'
                        elif day not in dic_gcal[ room ][ year ][ month ].keys() :
                            day_value_gcal = 'available'
                        else :
                            day_value_gcal = 'busy'
                        # Compare value
                        if day_value_itea == day_value_gcal or day_value_itea == 'nostatus' : # Ok
                            continue
                        elif day_value_gcal == 'busy' : # Google booked but not Itea
                            tmpList.append({'type':'itea-not-gcal-yes', 'room':room, 'year':year, 'month':month, 'day':day})
                        else : # Itea booked but not Google
                            tmpList.append({'type':'itea-yes-gcal-not', 'room':room, 'year':year, 'month':month, 'day':day})
        # Return list of issues
        return tmpList