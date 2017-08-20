
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import hashlib
import os
import arrow

from bot_interface import *
from bot_logging import logger, scheduler, scheduler_datetime

k_cache_size = 100
cached = dict()
ids_seq = []


"""
Every 5 hours bot makes a server request to obtain new info on the launches.
The next  ```k_cache_size```  are being cached  to  ```cached```.
```cached```   key : data
			   event['id'] : [fingerprint, msg]
	where msg is   ```generate_msg(event)```

To follow the sequence of the events  ```ids_seq```  
				stores ids in sequence of the launch time 
				(as it is uploaded from server)

Obtained info may not be not cached yet. 
So  ```check_up_to_date```  guarantees there is no double caching.
```get_cached_events```  returns ```events``` list
							with elements as {'msg':msg}

```remove_cached_by_id``` is scheduled 
the job to remove cached has 'id' == event['id']

"""

# event is cached
def check_up_to_date(event):
	c_event_hash = cached[id]['fingerprint']
	_hash = hashlib.sha1(str(event).encode()).hexdigest()

	if c_event_hash != _hash:
		if event['when'] != cached[event['id']]['when']:
			scheduler.modify_job(event['id'], 
				{'next_run_time':scheduler_datetime(event['when'].shift(minutes=1))})
		cache(event)
	
def cache(event, update_flag=False):
	fingerprint = hashlib.sha1(str(event).encode()).hexdigest()
	when = event['when'].timestamp
	cached[event['id']] = {'fingerprint': fingerprint, 'when':when, 'msg':generate_msg(event)}

def update_sequence(event_ids):
	ids_seq = event_ids[:]

def get_cached_events(count):
	events = []
	i = 0
	while i != count:
		msg = cached[ids_seq[i]]['msg']
		events.append({'msg':msg})
		i += 1
	return events

def remove_cached_by_id(id):
	del cached[id]
	if ids_seq[0] == id:
		del ids_seq[0]
	else:
		logger.error('ID mismatch. ids_seq[0] is not the same as the el to be removed.')
		logger.error('id %s is ' % id, 'not ' if id not in ids_seq else '', 'present in ids_seq')