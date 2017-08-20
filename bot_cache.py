
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import os
import hashlib
from bot_interface import *

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
```update_pos``` operates on ```ids_seq``` to make sure launch time didn't change
```get_cached_events```  returns ```events``` list
							with elements as {'msg':msg}
"""

# event is cached
def check_up_to_date(event):
	c_event_hash = cached[id][0]
	_hash = hashlib.sha1(str(event).encode()).hexdigest()

	if c_event_hash != _hash:
		cache(event)
		update_pos(event)
	
def cache(event, update_flag=False):
	fingerprint = hashlib.sha1(str(event).encode()).hexdigest()
	# if update_flag == True:
	# 	cached[event['id']]
	cached[event['id']] = [fingerprint, generate_msg(event)]

def update_pos(event):
	pass

def get_cached_events(count):
	events = []
	i = 0
	while i != count:
		msg = cached[ids_seq[i]][1]
		events.append({'msg':msg})
		i += 1
	return events