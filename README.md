# IteaToGcal

ITEA calendar (Gites de France) to Google agenda Python sync report and fix script

	./check-diff.py -h
	usage: check-diff.py [-h]
	                     [--action {list-diff,purge-google-of-itea-events,create-events-from-itea-to-google}]
    
	Report difference between ITEA and GCAL and propose to fix them
     
	optional arguments:
	  -h, --help            show this help message and exit
	  --action {list-diff,purge-google-of-itea-events,create-events-from-itea-to-google}
	                        Action to do


To list difference between Calendars :

	./check-diff.py --action list-diff
	+----------------------+------+-------+-----+--------------------------------------------+
	| Room                 | Year | Month | Day | Issue                                      |
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

To fix and create missing events in Google Calendar fron ITEA :

    ./check-diff.py --action create-events-from-itea-to-google
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+
	| Room             | Year | Month | Day | Issue                                                                                                                                                      |
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+
	| CAPUCINE         | 2016 |    02 |  17 | Event created : https://www.google.com/calendar/event?eid=bjRuZG5jaGQ4N29rMmpmZXMxMDg2a2JzczQgbGVzLWNvdXJ0aWxzLmNvbV9qYTZmcml0bGRrbTFiZ21yMzJsZXVlanBnMEBn |
	| CAPUCINE         | 2016 |    02 |  24 | Event created : https://www.google.com/calendar/event?eid=ZTJpdnA2c2l2bGtkdmdvYTVpcTdoOTU2NTQgbGVzLWNvdXJ0aWxzLmNvbV9qYTZmcml0bGRrbTFiZ21yMzJsZXVlanBnMEBn |
	| CHEVREFEUILLE    | 2016 |    02 |  27 | Event created : https://www.google.com/calendar/event?eid=YzM1aDI1MWJyNWFqZGMzN241cGI0NGYycGMgbGVzLWNvdXJ0aWxzLmNvbV9pdWpvYnMzamwyMTEydTJoMjlwYWY1b2ZzNEBn |
	| CHEVREFEUILLE    | 2016 |    03 |  20 | Event created : https://www.google.com/calendar/event?eid=cmZjODkybTljcThzcWN1MGNhbTNtNjVnbzggbGVzLWNvdXJ0aWxzLmNvbV9pdWpvYnMzamwyMTEydTJoMjlwYWY1b2ZzNEBn |
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+
	| Total : 4 row(s) |      |       |     |                                                                                                                                                            |
	+------------------+------+-------+-----+------------------------------------------------------------------------------------------------------------------------------------------------------------+

To delete all Google events created from ITEA calendar by this software :

	./check-diff.py --action purge-google-of-itea-events
	+--------------------+------+-------+-----+--------------------------------------------+
	| Room               | Year | Month | Day | Issue                                      |
	+--------------------+------+-------+-----+--------------------------------------------+
	| CAPUCINE           | 2016 |    02 |  16 | Itea calendar booked but Google agenda not |
	| CAPUCINE           | 2016 |    02 |  17 | Itea calendar booked but Google agenda not |
	| CAPUCINE           | 2016 |    02 |  21 | Itea calendar booked but Google agenda not |
	| CAPUCINE           | 2016 |    02 |  24 | Itea calendar booked but Google agenda not |
	+--------------------+------+-------+-----+--------------------------------------------+
	| Total : 4 row(s)   |      |       |     |                                            |
	+--------------------+------+-------+-----+--------------------------------------------+