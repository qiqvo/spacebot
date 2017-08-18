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
import requests
from emoji import emojize


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

user_timezone = ''
str_user_alarm_minutes_before = 'user_alarm_minutes_before'
ids_in_work_file = 'IDs.lst'
subscribers = 'subscribers.lst'


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
	update.message.reply_text("Hi! Nice to have you on board."
					"We are to take off the planet at... It's hard to tell not knowing your timezone.")
	user = update.message.from_user
	logger.info('new user %s' % user.first_name)
	help(bot, update)

def help(bot, update):
	help_message = 'usage: \n' \
			'/set_timezone -- to set the timezone\n' \
			'/next         -- to get the following launch\n' \
			'/next 4       -- to get the following 4 launches\n' \
			'/set_alarm 5  -- to set alarm on 5 minutes before the launch\n'
	update.message.reply_text('')

def timezone(bot, update, args):
	try:
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

def create_link(mode, next):
	source = 'https://launchlibrary.net/1.2/launch?'
	return source + 'mode=' + mode + '&' + 'next=' + next

# todo add "many"
def get_next_events(many): # many
	logging.info("Fetching launches!")
	
	r = requests.get(create_link('verbose', str(many))) # add many 
	events_lst = []

	#debug
	IDs_in_work.clear()

	if r.status_code == 200:
		for launch in r.json()['launches']:
			if launch['id'] in IDs_in_work:
				pass
			else: 
				IDs_in_work.append(launch['id'])
			
			event = {
				'id' : launch['id']
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
			events_lst.append(event)

	return events_lst


def generate_msg(props):
	message =  emojize(":rocket:", use_aliases=True)
	message += ' **' + props['name'] + '**' + '\n'
	message += 'A launch will happen ' + props['when'].humanize() + '!'
	message += ' at ' + props['when'].format('HH:mm') + '\n'
	message += 'Taking from **' + props['location'] + '**.\n'
	message += '**Mission description**\n' + props['description'] + '.\n\n'

#	if len(props['description']) > 0:
#		message += props['description'] + '\n'
	
	if len(props['urls']) > 0:
		message += 'Watch it here: \n'
		for url in props['urls']:
			message += '  • ' + url + '\n'
	else:
		message += 'Unfortunately there are no reported webcasts ' \
				   + emojize(':disappointed_relieved:', use_aliases=True)
	
	return message

# chat data is needed to implement user settings
def SendNext(bot, update, chat_data):
	SendNext(bot, update, [1], chat_data)

def SendNext(bot, update, args, chat_data):
	many = args[0]
	events = get_next_events(many)
	for event in events:
		SendNotif(bot, update.message.chat_id, event)
	
def ScheduleNotification(events, when):
	for event in events:
		job = job_queue.run_once(SendNotif,
			when=when, 
			context=[chat_id, event])


def update(bot, update, job_queue, chat_data):
	"""Adds a job to the queue"""
	chat_id = update.message.chat_id
	try:
		events = get_next_events()
		for event in events:
			try:
				before_minutes = chat_data[str_user_alarm_minutes_before]
				job_before_minutes = job_queue.run_once(SendNotif,
					when=props['when'].shift(minutes=-before_minutes).datetime.replace(tzinfo=None), 
					context=[chat_id, event])
				chat_data['job_before_minutes'] = job_before_minutes
			except KeyError as key_e:
				pass
	except Exception as e:
		logger.error(str(e))
		update.message.reply_text('Something went wrong!')


def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"' % (update, error))

def set_alarm(bot, update, args, chat_data):
	try:
		before = int(args[0])
		chat_data[str_user_alarm_minutes_before] = before
	except ValueError as val_e:
		update.message.reply_text('Enter integer!')


def main():

	# todo cache 10 next launches and update them every day
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

	# log all errors
	dp.add_error_handler(error)

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

