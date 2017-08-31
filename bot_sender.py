#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import telegram

from bot_cache import cache
from bot_interface import interface
from bot_logging import logger, scheduler
from bot_usersettings import users, Preferences

class Sender:
	"""
	firstly set up the bot!!
	"""
	def set_bot(self, bot):
		self.bot = bot

	def SendAll(self, event_id):
		from bot_base import base
		for user_id, user_pref in users.users.items():
			if user_pref.prefs['send_5_min_before_launch_alert']:
				event = base.get_event(event_id)
				msg = interface.generate_msg(event, alert=True, user_pref=user_pref.prefs)
				if msg:
					self.Send(user_id, msg)


	# TODO check if telegram.ParseMode.MARKDOWN works correctly
	def Send(self, user_id, msg):
		self.bot.send_message(user_id, text=msg,
				parse_mode=telegram.ParseMode.MARKDOWN)
			
	def SendNext(self, user_id, count):
		from bot_base import base
		events = base.get_next_events(count)
		for event in events:
			msg = interface.generate_msg(event, users.users[user_id].prefs)
			self.Send(user_id, msg)

sender = Sender()