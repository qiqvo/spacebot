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

	# TODO add failreason, holdreason
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
		if past:
			message += ' Launch was held on: ' + props['when'].format('YYYY-MM-DD HH:mm:ss ZZ') + '.\n'
		else:
			if alert:
				message += ' *Launch is going to happen in some minutes!* '
		message += ' *' + props['name'] + '*' + '\n'

		if not alert and not past:
			message += 'A launch will happen _' + props['when'].humanize() + '_! '
			message += 'I mean ' + props['when'].format('YYYY-MM-DD HH:mm:ss ZZ') + '\n'

		if past:
			message += 'Taken from *'
		else:
			message += 'Taking from *'

		message += props['location'] + '*.\n'

		message += '*Mission description*\n' + Interface.generate_description(props['missions']) + '\n\n'


		if props['urls']:
			message += 'Watch it here: \n' if not past else 'You could have watched it here: \n'
			for url in props['urls']:
				message += '  • [' + url + '](' + url +')\n'
		else:
			message += 'Unfortunately there '
			message += 'are' if not past else 'were'
			message += ' no reported webcasts ' \
					   + emojize(':disappointed_relieved:', use_aliases=True)

		return message


	welcome_message = 'Hi! Nice to have you on board. '  \
						'We are to take off the planet at... '

	help_message =  'usage: \n' \
				'/help                  -- to get this msg\n' \
				'/next         			-- to get the following launch\n' \
				'/next <num> 			-- to get the following 4 launches\n' \
				'/send_uncertain_launches -- to send uncertain launches. Send once more to discard\n' \
				'/subscribe             -- to get alerts 5 min before the launch\n' \
				'/unsubscribe           -- to disable it\n' \
				"/last_week				-- to send last week's launches\n" \
				'/stop 					-- to stop the bot\n'

	# BOTfather format
	'''
	help - to get this msg
	next - to get the following launch
	send_uncertain_launches - to send uncertain launches. Send once more to discard
	subscribe - to get alerts 5 min before the launch
	unsubscribe - to disable it
	stop - to stop the bot
	last_week - to send last week's launches
	'''
	# TODO add exit_message
	exit_message = 'ddddd'

	send_uncertain_launches_activated_msg = 'You have actived sending of uncertain launches.'
	send_uncertain_launches_deactivated_msg = 'You have deactivated sending of uncertain launches.'

	# TODO write subscibe answer msg
	subscribe_message = 'bla-fghjkl-bla' # you will be subscribed in 15 minutes at most! Thanks!
	unsubscribe_message = 'bla-bla-bla' # you will be unsubscribed in 15 minutes at most!
	

interface = Interface()