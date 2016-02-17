# IteaToGcal

ITEA calendar (Gites de France) to Google agenda Python sync report and fix

To install prerequisites (Python lib) :

    apt-get install libxml2-dev libxslt-dev python-dev # For Debian
	pip install httplib2 terminaltables google-api-python-client icalendar requests lxml

Usage :

	./check-diff.py -h
	usage: check-diff.py [-h] [--noauth_local_webserver]
	                     [--action {list-diff,create-google-events-from-itea,delete-google-events-from-itea}]
    
	Report difference between ITEA and GCAL and propose to fix them
     
	optional arguments:
	  -h, --help            show this help message and exit
	  --noauth_local_webserver
	                        Needed for first execution (Google Agenda
	                        authentication)
	  --action {list-diff,create-google-events-from-itea,delete-google-events-from-itea}


To list difference between calendars :

	./check-diff.py --action list-diff
	######### Date : 2016-02-17 - App : IteaToGcal #########
	- Start time : 2016-02-17 03:49:44
	- Finish time : 2016-02-17 03:50:03
	- Delta time : 18 second(s)
	+----------------------+------+-------+-----+--------------------------------------------+
	| Room                 | Year | Month | Day | Message                                    |
	+----------------------+------+-------+-----+--------------------------------------------+
	| COLOQUINTE           | 2016 |    02 |  26 | ITEA calendar booked but Google agenda not |
	| COLOQUINTE           | 2016 |    02 |  28 | ITEA calendar booked but Google agenda not |
	| COLOQUINTE           | 2016 |    02 |  14 | ITEA calendar booked but Google agenda not |
	| CAPUCINE             | 2016 |    10 |  30 | ITEA calendar booked but Google agenda not |
	| CAPUCINE             | 2016 |    10 |  02 | ITEA calendar booked but Google agenda not |
	| CAPUCINE             | 2016 |    10 |  09 | ITEA calendar booked but Google agenda not |
	| CAPUCINE             | 2016 |    10 |  23 | ITEA calendar booked but Google agenda not |
	+----------------------+------+-------+-----+--------------------------------------------+
	| Total :   7 issue(s) |      |       |     |                                            |
	+----------------------+------+-------+-----+--------------------------------------------+

To fix and create missing events in Google Calendar from ITEA :

    ./check-diff.py --action create-google-events-from-itea
	######### Date : 2016-02-17 - App : IteaToGcal #########
	- Start time : 2016-02-17 03:49:44
	- Finish time : 2016-02-17 03:50:03
	- Delta time : 18 second(s)
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+
	| Room             | Year | Month | Day | Message                                                                                                                                                    |
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+
	| CAPUCINE         | 2016 |    02 |  17 | Event created : https://www.google.com/calendar/event?eid=bjRuZG5jaGQ4N29rMmpmZXMxMDg2a2JzczQgbGVzLWNvdXJ0aWxzLmNvbV9qYTZmcml0bGRrbTFiZ21yMzJsZXVlanBnMEBn |
	| CAPUCINE         | 2016 |    02 |  24 | Event created : https://www.google.com/calendar/event?eid=ZTJpdnA2c2l2bGtkdmdvYTVpcTdoOTU2NTQgbGVzLWNvdXJ0aWxzLmNvbV9qYTZmcml0bGRrbTFiZ21yMzJsZXVlanBnMEBn |
	| CHEVREFEUILLE    | 2016 |    02 |  27 | Event created : https://www.google.com/calendar/event?eid=YzM1aDI1MWJyNWFqZGMzN241cGI0NGYycGMgbGVzLWNvdXJ0aWxzLmNvbV9pdWpvYnMzamwyMTEydTJoMjlwYWY1b2ZzNEBn |
	| CHEVREFEUILLE    | 2016 |    03 |  20 | Event created : https://www.google.com/calendar/event?eid=cmZjODkybTljcThzcWN1MGNhbTNtNjVnbzggbGVzLWNvdXJ0aWxzLmNvbV9pdWpvYnMzamwyMTEydTJoMjlwYWY1b2ZzNEBn |
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+
	| Total : 4 row(s) |      |       |     |                                                                                                                                                            |
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+

To fix and delete overload events in Google Calendar from ITEA :

	./check-diff.py --action delete-google-events-from-itea
	######### Date : 2016-02-17 - App : IteaToGcal #########
	- Start time : 2016-02-17 03:49:44
	- Finish time : 2016-02-17 03:50:03
	- Delta time : 18 second(s)
	+------------------+------+-------+-----+-------------------------------------+
	| Room             | Year | Month | Day | Message                             |
	+------------------+------+-------+-----+-------------------------------------+
	| CAPUCINE         | 2016 |    03 |  08 | Event deleted : Test 1              |
	|                  |      |       |     | Event deleted : Test 2              |
	| CAPUCINE         | 2016 |    03 |  09 | Event deleted : Test 3              |
	| CAPUCINE         | 2016 |    03 |  10 | Google Agenda event already deleted |
	+------------------+------+-------+-----+-------------------------------------+
	| Total : 3 row(s) |      |       |     |                                     |
	+------------------+------+-------+-----+-------------------------------------+