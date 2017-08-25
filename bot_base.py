#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import arrow
import requests

from bot_cache import cache
from bot_logging import logger, scheduler
from bot_sender import sender
from bot_usersettings import users


# Modes are list, summary, verbose
def create_link(mode, next):
	source = 'https://launchlibrary.net/1.2/launch?'
	return source + 'mode=' + mode + '&' + 'next=' + next

# returns raw launches!
def pick_info(start=0, end=cache.k_cache_size):
	logger.info("Picking launches...")
	r = requests.get(create_link(mode='verbose', next=str(end)))

	if r.status_code == 200:
		return (r.json()['launches'])[start : end]
	else:
		logger.error('Error: bad request, while picking')
		return []

def create_event(launch):
	event = {
		'id' : launch['id'],
		"when": arrow.get(launch['isonet'], "YYYYMMDDTHHmmss?"),
		"name": launch['name'],
		"probability": launch['probability'], # -1 for unknown
		"urls": launch['vidURLs'],
		#"pic": launch['rocket']['imageURL'],
		#"pic_sizes": launch['rocket']['imageSizes'],
		"missions_count": len(launch['missions']),
		"description": launch['missions'][0]['description'],
		#"rocket": launch['rocket']['name']
		'location': launch['location']['pads'][0]['name'] 
	}

	return event

class Base:
	"""
	a table which is sorted by 'time'
	id#time# other event props:...name#...
	"""
	k_table_size = 100  
	table = [None] * k_table_size
	jobs = []

	def update(self):
		logger.info("Updating launches")
		launches = pick_info()
		
		# TODO dont reset the whole table -- just update the content and sort by date
		logger.info('\tresetting table of events')
		num = 0
		for launch in launches:
			event = create_event(launch)
			self.table[num] = event
			num += 1
		
		# TODO dont remove prev jobs, try to update the ones
		logger.info('\tresetting jobs\n\t\tRemoving prev jobs')
		for job in self.jobs:
			job['job_start'].remove()
			job['job_remove'].remove()
		self.jobs.clear()

		logger.info('\t\tSetting new jobs')
		for event in self.table:
			job_start = scheduler.add_job(sender.SendAll,
				trigger='date', run_date=event['when'].shift(minutes=-5).datetime,
				args=[event['id']])
			job_remove = scheduler.add_job(self.remove_first, 
				trigger='date', run_date=event['when'].shift(minutes=1).datetime,
				args=[event['id']])

			self.jobs.append({
				'id': event['id'], 
				'job_start' :  job_start,
				'job_remove' : job_remove})

		logger.info('Update is done!')

	def remove_first(self):
		logger.info('removing the first event in table')
		if self.table[0]['when'] < arrow.now():
			logger.warning('the event you are removing is not yet come')

		del self.table[0]

	def get_next_events(self, count):
		return self.table[:count]

	def get_event(self, event_id):
		for event in self.table:
			if event['id'] is event_id:
				return event

base = Base()
