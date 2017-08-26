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
	# key 'msg' contains cached msg
	@staticmethod
	def generate_msg(props, user_pref=None):
		if 'msg' in props:
			return props['msg']

		message =  emojize(":rocket:", use_aliases=True)
		message += ' **' + props['name'] + '**' + '\n'
		message += 'A launch will happen ' + props['when'].humanize() + '!'
		message += ' at ' + props['when'].format('HH:mm') + '\n'
		message += 'Taking from **' + props['location'] + '**.\n'
		message += '**Mission description**\n' + props['description'] + '.\n\n'

		if len(props['urls']) > 0:
			message += 'Watch it here: \n'
			for url in props['urls']:
				message += '  • ' + url + '\n'
		else:
			message += 'Unfortunately there are no reported webcasts ' \
					   + emojize(':disappointed_relieved:', use_aliases=True)

		return message

	welcome_message = 'Hi! Nice to have you on board. '  \
						'We are to take off the planet at... '  \
						"It's hard to tell not knowing your timezone."
	help_message =  'usage: \n' \
				'/help                  -- to get this msg\n' \
				'/next         			-- to get the following launch\n' \
				'/next 4       			-- to get the following 4 launches\n' \
				'/send_uncertain_launches yes -- to send ...'

	# TODO write subscibe answer msg 
	subscribe_message = 'bla-bla-bla'

interface = Interface()