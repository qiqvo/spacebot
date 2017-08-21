#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Basics are copied from:
https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py
and 
https://github.com/elamperti/spacebot/blob/master/spacebot.py
"""


"""
implement folloing TODO instr
	# TODO user settings: if to send msgs without videos
	# 					  if to send uncertain launches
	# 					  if to send pictures in what resolution is preferable

user_preferences should be saved in a file
#user_id  --   preference code 

pref code  is a num which should be seen as bits

```users``` is a list of dicts
			user is [{'id':###, 'pref': Preferences}, ...]
"""

class Preferences:
	def __init__(self, **kwargs
		#send_uncertain_launches
		#,...
	):
		if 'prefcode' in kwargs:
			self._init_with_prefcode(kwargs['prefcode'])
		else:
			# TODO check if the order is right!!
			self._init_with_args([val for key, val in kwargs])
			self.code = self.generate_code() 
	
	def _init_with_args(self, *args):
		self.send_uncertain_launches = args[0]
		# ... 
		
	def _init_with_prefcode(self, prefcode):
		bin_code = "{0:b}".format(prefcode)
		args = [bool(c) for c in bin_code[::-1]]
		self._init_with_args(args)
		self.code = int(prefcode)

	def generate_code(self):
		"""returns int"""
		bin_code = '1' if self.send_uncertain_launches else '0'
		return int(bin_code, 2)

class Users:
	"""
	```users``` is a list of dicts
			users is [{'id':###, 'pref': Preferences}, ...]
	"""
	users = set()
	users_filename = 'users.lst'
	tmp_users_filename = 'tmp_users.lst'

	def add_user(self, user_id, **pref):
		u_pref = Preferences(kwargs=pref)
		with open(self.users_filename, 'a') as uf:
			uf.print(user_id, u_pref.code)

		self.users.add({'id':user_id, 'pref':u_pref })

# TODO union modify and remove funcs 
# 		send not only one id, but a list
#		EXP: users should update every 15 min
	def remove_user(self, user_id):
		self._update_users(removed=[user_id])
		self._update_file(removed=[user_id])

	def modify_user(self, user_id, pref):
		self._update_users(modify_upref={user_id:pref})
		self._update_file(modify_upref={user_id:pref})

	def _update_users(self, *removed, **modify_upref):
		"""
		removed == list of ids
		modify_upref == dict {'id':code, ...}
		"""
		_add = []
		for user in self.users:
			if user['id'] in removed:
				self.users.remove(user)
				pass
			if user['id'] in modify_upref:
				self.users.remove(user)
				_add.append({'id': user['id'], 'pref': modify_upref[user['id']]})
		
		# mutex like structure: 
		for change in _add:
			self.users.add(change)
				

	def _update_file(self, *removed, **modify_upref):
		"""
		removed == list of ids
		modify_upref == dict {'id':code, ...}
		"""
		with open(self.users_filename, 'r') as uf, open(self.tmp_users_filename, 'w') as tuf:
			for line in uf:
				user_id, code = line.split()
				if user_id in removed:
					pass

				print(user_id, modify_upref[user_id] if user_id in modify_upref else code, file=tuf)

		# TODO rename files
		# copy from tmp to working
		with open(self.tmp_users_filename, 'r') as tuf, open(self.users_filename, 'w') as uf:
			for line in tuf:
				print(line, file=uf)

		# clear tmp file
		open(self.tmp_users_filename, 'w').close()