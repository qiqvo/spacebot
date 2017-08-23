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
from telegram.ext import CommandHandler, Job, Updater

from bot_info import get_next_events, update
from bot_interface import *
from bot_logging import logger, scheduler
from bot_usersettings import users

def timezone(bot, update, args, chat_data):
	try:
		update.message.reply_text()		
		if not args[0]:
			raise Exception('no input in timezone')
		else:
			a = arrow.now().replace(tzinfo=args[0])
			user_timezone = a.tzinfo
		
		update.message.reply_text('Set to %s.' % user_timezone)

	except Exception as e:
		logger.error(str(e))
		user_timezone = '+00:00'
		update.message.reply_text('Something went wrong. Try to enter it once more')

def subscribe(bot, update, chat_data):
	users.add_user(update.message.chat_id, 
				pref={'send_uncertain_launches': True})

def send_uncertain_launches(bot, update, args, chat_data):
	if args[0] == 'yes':
		chat_data['send_uncertain_launches'] = True

	user_id = update.message.chat_id
	users.change(modify=[user_id, ['send_uncertain_launches', True]])

# job.context = [chat_id, event]
def SendNotif(bot, chat_id, event):
	msg = generate_msg(event)
	bot.send_message(chat_id, text=msg, parse_mode=telegram.ParseMode.MARKDOWN)

# chat data is needed to implement user settings
def SendNext(bot, update, chat_data, args=[1]):
	count = int(args[0])
	events = get_next_events(count)
	for event in events:
		SendNotif(bot, update.message.chat_id, event)
	
def error(bot, update, error):
	logger.warning('Update "%s" caused error "%s"' % (update, error))

def start(bot, update):
	update.message.reply_text(welcome_message)
	user = update.message.from_user
	logger.info('new user %s' % user.first_name)
	help(bot, update)

def help(bot, update):
	update.message.reply_text(help_message)
	
def main():
	# TODO create event class with event remover (scheduler) 
	# TODO get timezone from 
	# 				https://maps.googleapis.com/maps/api/timezone/json?location=38.908133,-77.047119&timestamp=1458000000
	# TODO discuss line 94 ```run_date=event['when'].shift(minutes=1),```
	# TODO show notif of the ongoing launch mission if one is happening while your chat 
	# TODO probability coefs
	# TODO if no vid, send pic 
	# TODO add user setting chat with 15 min update and 'only last change matters'
	# TODO user settings: if to send msgs without videos
	# 					  if to send uncertain launches
	# 					  if to send pictures in what resolution is preferable
	# TODO make subscriber list and 
	#      send them all the notification in 30 mins
	# TODO make available more info about the launch 
	#	   maybe send launch id and make a func '/more_info id 1234'
	# TODO make a full python lib for the source site ;;launchlibrary;;

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
	#dp.add_handler(CommandHandler("set_alarm", set_alarm, pass_args=True, pass_chat_data=True))
	dp.add_handler(CommandHandler('next', SendNext, 
								pass_args=True, 
								pass_chat_data=True))
	
	#dp.add_handler()
	dp.add_handler(CommandHandler('subscribe', subscribe, pass_chat_data=True))
	dp.add_handler(CommandHandler('send_uncertain_launches', send_uncertain_launches, 
								pass_chat_data=True, pass_args=True))

	# log all errors
	dp.add_error_handler(error)

	scheduler.add_job(update, 'interval', hours=5)
	
	users.get_from_file()
	scheduler.add_job(users._change, 'interval', minutes=15)
	
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
