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

from bot_logging import logger, scheduler
from bot_sender import sender
from bot_usersettings import users
from bot_lastweek import lastweek


# Modes are list, summary, verbose
def create_link(mode, next):
	source = 'https://launchlibrary.net/1.2/launch?'
	return source + 'mode=' + mode + '&' + 'next=' + next

# returns raw launches!
def pick_info(count):
	logger.info("Picking launches...")
	r = requests.get(create_link(mode='verbose', next=str(count)))

	if r.status_code == 200:
		return (r.json()['launches'])
	else:
		logger.error('Error: bad request, while picking')
		return []

def create_event(launch):
	"""
	event
		id is num
		when is arrow time (T-0 time)
		name is str   (name of launch)
		probability is num (-1 for unknown)
		urls is a list
		missions is a list (in each may be present ['description'])
		pads is a list
		location is a str (country name)
	"""
	event = {
		'id' : launch['id'],
		"when": arrow.get(launch['isonet'], "YYYYMMDDTHHmmss?"),
		"name": launch['name'],
		"probability": launch['probability'], # -1 for unknown
		"urls": launch['vidURLs'],
		#"pic": launch['rocket']['imageURL'],
		#"pic_sizes": launch['rocket']['imageSizes'],
		"missions": launch['missions'],
		#"rocket": launch['rocket']['name']
		'pads': launch['location']['pads'],
		'location' : launch['location']['name'],
		'failreason' : launch['failreason'],
		'holdreason' : launch['holdreason']
	}

	return event

class Base:
	"""
	a table which is sorted by 'time'
	id#time# other event props:...name#...
	"""
	k_table_size = 100
	table = []
	jobs = []

	def update(self):
		logger.info("Updating launches")
		launches = pick_info(self.k_table_size)

		# TODO dont reset the whole table -- just update the content and sort by date
		logger.info('resetting table of events')
		logger.info('Removing prev entries')
		self.table.clear()
		logger.info('Setting new events')
		for launch in launches:
			event = create_event(launch)
			if event['when'] > arrow.now():
				self.table.append(event)
		
		# TODO dont remove prev jobs, try to update the ones
		logger.info('resetting jobs')
		logger.info('Removing prev jobs')
		for job in self.jobs:
			job['job_start'].remove()
			job['job_remove'].remove()
		self.jobs.clear()

		logger.info('Setting new jobs')
		for event in self.table:
			job_start = scheduler.add_job(sender.SendAll,
				trigger='date', run_date=event['when'].shift(minutes=-5).datetime,
				args=[event['id']])
			job_remove = scheduler.add_job(self.remove_first,
				trigger='date', run_date=event['when'].shift(minutes=1).datetime)

			self.jobs.append({
				'id': event['id'],
				'job_start' :  job_start,
				'job_remove' : job_remove})

		logger.info('Update is done!')

	def remove_first(self):
		logger.info('removing the first event in table')
		if self.table[0]['when'] < arrow.now():
			logger.warning('the event you are removing is not yet come')
		else:
			lastweek.add_event(self.table[0])

		del self.table[0]

	def get_next_events(self, count):
		if count > self.k_table_size:
			launches = pick_info(count)
			events = []
			for launch in launches:
				event = create_event(launch)
				events.append(event)
			return events
		else:
			return self.table[:count]

	def get_event(self, event_id):
		for event in self.table:
			if event['id'] is event_id:
				return event

base = Base()
