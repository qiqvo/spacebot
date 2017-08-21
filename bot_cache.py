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
from bot_logging import logger, scheduler


class Cache:
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
	k_cache_size = 100
	cached = dict()
	ids_seq = []

	# event is cached
	def check_up_to_date(self, event):
		c_event_hash = self.cached[id]['fingerprint']
		_hash = hashlib.sha1(str(event).encode()).hexdigest()

		if c_event_hash != _hash:
			if event['when'].timestamp != self.cached[event['id']]['when']:
				scheduler.modify_job(event['id'], 
					{ 'next_run_time': event['when'].shift(minutes=1) })
			self.cache(event, fingerprint=_hash)
	
	def cache(self, event, fingerprint=''):
		if not fingerprint:
			fingerprint = hashlib.sha1(str(event).encode()).hexdigest()
		when = event['when'].timestamp
		self.cached[event['id']] = {'fingerprint': fingerprint, 'when':when, 'msg':generate_msg(event)}

	def update_sequence(self, event_ids):
		self.ids_seq = event_ids[:]

	def get_cached_events(self, count):
		events = []
		i = 0
		while i != count:
			msg = self.cached[self.ids_seq[i]]['msg']
			events.append({'msg':msg})
			i += 1
		return events

	def remove_cached_by_id(self, id):
		del self.cached[id]
		if self.ids_seq[0] == id:
			del self.ids_seq[0]
		else:
			logger.error('ID mismatch. ids_seq[0] is not the same as the el to be removed.')
			logger.error('id %s is ' % id, 'NOT ' if id not in self.ids_seq else '', 'present in ids_seq')


cache = Cache()