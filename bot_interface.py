#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

import arrow
from emoji import emojize

class Interface:
	@staticmethod
	def generate_description(missions):
		descr = ''
		for mission in missions:
			descr += '_' + mission['typeName'] + '_    ' + mission['name'] + '\n' + mission['description'] + '\n'

		return descr


	# TODO probability coefs
	# TODO if no vid, send pic
	@staticmethod
	def generate_msg(props, alert=False, user_pref=None, past=False):
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

			if past:
				failreason
				holdreason
		"""
		message =  emojize(":rocket:", use_aliases=True)
		if alert:
			message += ' *Launch is going to happen in some minutes!* '
		message += ' *' + props['name'] + '*' + '\n'

		if not alert:
			message += 'A launch will happen _' + props['when'].humanize() + '_! '
			message += 'I mean ' + props['when'].format('YYYY-MM-DD HH:mm:ss ZZ') + '\n'

		message += 'Taking from *' + props['location'] + '*.\n'

		message += '*Mission description*\n' + Interface.generate_description(props['missions']) + '\n\n'

		if props['urls']:
			message += 'Watch it here: \n'
			for url in props['urls']:
				message += '  • [' + url + '](' + url +')\n'
		if past:
			if holdreason: message += 'The launch has been held. Reason: ' + holdreason 
			if failreason: message += 'Unfortunately, the launch failed. Reason: ' + failreason
		else:
			message += 'Unfortunately there '
			message += 'are' if not past else 'were'
			message += ' no reported webcasts ' \
					   + emojize(':disappointed_relieved:', use_aliases=True)

		return message

	welcome_message = 'Hi! Nice to have you on board. '  \
						'We are to take off the planet at... \n' \
						'If you have any questions, ideas or difficulties using Spacebot, feel free to contact @qiqvo.'

	help_message =  'usage: \n' \
				'/help                  -- to get this message\n' \
				'/next         			-- to get the next launch\n' \
				'/next <num> 			-- to get the next <num> launches\n' \
				'/send_uncertain_launches -- to send uncertain launches. Send once more to discard' \
				'/subscribe             -- to get notifications 5 mins before a launch happens' \
				'/unsubscribe           -- to disable notifications' \
				'/stop 					-- to stop the bot'

	# BOTfather format
	'''
	help - to get this msg
	next - to get the following launch
	send_uncertain_launches - to send uncertain launches. Send once more to discard
	subscribe - to get alerts 5 min before the launch
	unsubscribe - to disable it
	stop - to stop the bot
	'''
	exit_message = 'Bot stopped. If there are any problems you encountered and would like to report, please contact @qiqvo. Thank you for using Spacebot!'

	send_uncertain_launches_activated_msg = 'You have actived sending of uncertain launches.'
	send_uncertain_launches_deactivated_msg = 'You have deactivated sending of uncertain launches.'

	subscribe_message = 'Thank you for subscribing! Please note that it usually takes us around 15 minutes to subscribe you to our notifications.' 
	unsubscribe_message = 'You will be unsubscribed in 15 minutes at most.'


interface = Interface()
