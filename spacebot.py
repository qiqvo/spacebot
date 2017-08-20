#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import os
import telegram
from telegram.ext import Updater, CommandHandler, Job

import logging

import arrow
import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from bot_cache import *
from bot_interface import *


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

user_timezone = ''

# in chat_data dict
_user_alarm_minutes_before = 'user_alarm_minutes_before'
_subscriber_5_min_before_the_launch = 's_5mb'


subscribers_filename = 'subscribers_5mb.lst' # list of "5 minutes before the launch"-subscribers
subscribers = []

def timezone(bot, update, args):
	try:
		update.message.reply_text()		
		if not args[0]:
			raise Exception('no input in timezone')
		else:
			a = arrow.now().replace(tzinfo=args[0])
			user_timezone = a.tzinfo
		
		update.message.reply_text('Set to %s.' % user_timezone)

	except Exception as e:
		logging.error(str(e))
		user_timezone = '+00:00'
		update.message.reply_text('Something went wrong. Try to enter it once more')

# context = [chat_id, event]
def SendNotif(bot, job):
	"""Function to send the alarm message"""
	SendNotif(bot, job.context[0], job.context[1])

def SendNotif(bot, chat_id, event):
	msg = generate_msg(event)
	bot.send_message(chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

# chat data is needed to implement user settings
def SendNext(bot, update, chat_data):
	SendNext(bot, update, [1], chat_data)

def SendNext(bot, update, args, chat_data):
	count = args[0]
	events = get_next_events(count)
	for event in events:
		SendNotif(bot, update.message.chat_id, event)
	
def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"' % (update, error))

# Modes are list, summary, verbose
def create_link(mode, next):
	source = 'https://launchlibrary.net/1.2/launch?'
	return source + 'mode=' + mode + '&' + 'next=' + next

def get_next_events(count):
	events = get_cached_events(count) if count < k_cache_size else get_cached_events(k_cache_size)
	if count > k_cache_size:
		launches = pick_info(start=k_cache_size, end=(count+1))
		for launch in launches:
			events.append(create_event(launch))
		
	return events

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

# returns raw launches!! Its not the same as events
def pick_info(start=0, end=k_cache_size):
	logging.info("Picking...")
	r = requests.get(create_link(mode='verbose', next=str(to)))

	if r.status_code == 200:
		return (r.json()['launches'])[start : end]
	else:
		logger.error('Error: bad request, while picking')
		return []


def update():
	logging.info("Updating launches")
	
	launches = pick_info()

	# clean cached ids which are no longer present
	_first = 0
	while launches[0]['id'] != cached_ids[_first]:
		_first += 1
	if _first != 0:
		cached_ids[_first:]

	for launch in launches:
		event = create_event(launch)
		if int(event['id']) in cache_dct:
			check_up_to_date(event)
		else: 
			cache(event)


def start(bot, update):
	update.message.reply_text(welcome_message)
	user = update.message.from_user
	logger.info('new user %s' % user.first_name)
	help(bot, update)

def help(bot, update):
	update.message.reply_text(help_message)


	
def main():
	# todo bot_cache update pos func!
	# todo clean cached ids as soon as start occured
	# todo show notif of the ongoing launch mission if one is happening while your first chat 
	# todo probability coefs
	# todo if no vid, send pic 
	# todo user settings: if to send msgs without videos
	# 					  if to send uncertain launches
	# 					  if to send pictures in what resolution is preferable
	# todo make subscriber list and 
	#      send them all the notification in 30 mins
	# todo make available more info about the launch 
	#	   maybe send launch id and make a func '/more_info id 1234'
	# todo make a full python lib for the source site ;;launchlibrary;;

	token = ''
	if os.path.isfile('_token.token'):
		with open('_token.token', 'r') as tokenFile:
			token = tokenFile.read().replace('\n', '')

	updater = Updater(token)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", start))
	dp.add_handler(CommandHandler("update", update,
								  pass_job_queue=True,
								  pass_chat_data=True))
	#dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))
	
	dp.add_handler(CommandHandler("set_timezone", timezone, pass_args=True))
	dp.add_handler(CommandHandler("set_alarm", set_alarm, pass_args=True, pass_chat_data=True))
	dp.add_handler(CommandHandler('next', SendNext, pass_args=True, pass_chat_data=True))
	dp.add_handler(CommandHandler('next', SendNext, pass_chat_data=True))
	
	
	dp.add_handler()
	#dp.add_handler(CommandHandler('subscribe', subscribe, pass_chat_data=True))

	# log all errors
	dp.add_error_handler(error)

	# to archive updating without user, we should use schedule module
	scheduler = BackgroundScheduler()
	update()
	scheduler.add_job(update, 'interval', hours=5)
	scheduler.start()

	# Start the Bot
	updater.start_polling()

	# Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
	# SIGABRT. This should be used most of the time, since start_polling() is
	# non-blocking and will stop the bot gracefully.
	updater.idle()


if __name__ == '__main__':
	main()

# def unset(bot, update, chat_data):
# 	"""Removes the job if the user changed their mind"""
# 
# 	if 'job' not in chat_data:
# 		update.message.reply_text('You have no active timer')
# 		return
# 
# 	job = chat_data['job']
# 	job.schedule_removal()
# 	del chat_data['job']
# 
# 	update.message.reply_text('Timer successfully unset!')

# def update(bot, update, job_queue, chat_data):
# 	"""Adds a job to the queue"""
# 	chat_id = update.message.chat_id
# 	try:
# 		events = get_next_events()
# 		for event in events:
# 			if _user_alarm_minutes_before in chat_data:
# 				before_minutes = chat_data[_user_alarm_minutes_before]
# 				job_before_minutes = job_queue.run_once(SendNotif,
# 					when=props['when'].shift(minutes=-before_minutes).datetime.replace(tzinfo=None), 
# 					context=[chat_id, event])
# 				chat_data['job_before_minutes'] = job_before_minutes
# 	except Exception as e:
# 		logger.error(str(e))
# 		update.message.reply_text('Something went wrong!')