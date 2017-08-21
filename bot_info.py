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
from bot_usersettings import users


# Modes are list, summary, verbose
def create_link(mode, next):
	source = 'https://launchlibrary.net/1.2/launch?'
	return source + 'mode=' + mode + '&' + 'next=' + next

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

	scheduler.add_job(cache.remove_cached_by_id, trigger='date', 
				run_date=event['when'].shift(minutes=1).datetime,
				args=[event['id']], id=event['id'])

	return event

# returns raw launches!! Its not the same as events
def pick_info(start=0, end=cache.k_cache_size):
	logger.info("Picking...")
	r = requests.get(create_link(mode='verbose', next=str(end)))

	if r.status_code == 200:
		return (r.json()['launches'])[start : end]
	else:
		logger.error('Error: bad request, while picking')
		return []


def update():
	logger.info("Updating launches")
	
	launches = pick_info()

	_ids = []
	for launch in launches:
		event = create_event(launch)
		_ids.append(event['id'])
		if event['id'] in cache.cached:
			cache.check_up_to_date(event)
		else:
			cache.cache(event)
	
	cache.update_sequence(_ids)

def get_next_events(count):
	events = cache.get_cached_events(count=count) if count < cache.k_cache_size else cache.get_cached_events(cache.k_cache_size)
	if count > cache.k_cache_size:
		launches = pick_info(start=cache.k_cache_size, end=(count+1))
		for launch in launches:
			events.append(create_event(launch))
		
	return events
