
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


cached_ids_filename = 'IDs.lst'
cache_last_num = 0
cache_file_format = '.cch'
cache_sign_file = 'cache.sign'
dir_cache = os.open('cache', O_RDONLY)
k_cache_size = 100
cache_dct = dict()

def cache_dir_opener(path, flags):
	return os.open(path, flags, dir_fd=dir_cache)

def get_event_hash(id):
	with open(cache_sign_file, 'r') as csf:
		for line in csf:
			if line.split()[0] == id:
				return line.split()[2]

	return ''

# event is cached
def check_up_to_date(event):
	c_event_hash = get_event_hash(event['id'])
	_hash = hashlib.sha1(str(event).encode()).hexdigest()

	if c_event_hash != _hash:
		cache(event, update_flag=True)
	
# update_flag == event is needed to be recached
def cache(event, update_flag=False):
	filename = ''
	id = event['id']
	if update_flag:
		filename = str(cache_dct[id])
	else:
		filename = str(cache_last_num) 

	filename += cache_file_format
	fingerprint = hashlib.sha1(str(event).encode()).hexdigest()

	with open(filename, 'w', opener=cache_dir_opener) as cf:
		print(fingerprint, file=cf)
		print(generate_msg(event), file=cf)
	
	if not update_flag:
		with open(cache_sign_file, 'a') as sf:
			print(id, cache_last_num, fingerprint, file=sf)

		cache_dct[id] = cache_last_num
		cache_last_num +=1

def get_cached_events(count):
	events = []
	while count > 0:
		filename = count + cache_file_format
		msg = ''
		with open(filename, 'r', opener=cache_dir_opener) as cf:
			cf.read()
			for line in cf:
				msg += line
		events.append({'msg':msg})
		count -= 1
	return events