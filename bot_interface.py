#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""

from emoji import emojize
import arrow

# key 'msg' contains cached msg
def generate_msg(props):
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

welcome_message = 'Hi! Nice to have you on board.'  \
					'We are to take off the planet at...'  \
					"It's hard to tell not knowing your timezone."
help_message =  'usage: \n' \
			'/set_timezone +00:00 	-- to set the timezone UTC\n' \
			'/next         			-- to get the following launch\n' \
			'/next 4       			-- to get the following 4 launches\n' \
			'/set_alarm 5  			-- to set alarm on 5 minutes before the launch\n'
