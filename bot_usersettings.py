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

	```users``` is a dict
			users is {'id': Preferences, ...}
"""

class Preferences:
	"dict of  {'what':val, ...}"
	prefs = dict()
	pref_names = ['send_uncertain_launches']
	# code = int 

	def __init__(self, kwargs):
		if 'prefcode' in kwargs:
			self._init_with_prefcode(kwargs['prefcode'])
			self.code = kwargs['prefcode']
		else:
			for name, val in kwargs.items():
				self.set(what=name, val=val)
			
			self.code = self.generate_code() 
	
	def _init_with_prefcode(self, prefcode):
		"""
		prefcode is str
		function generates a kwargs for __init__ 
		"""
		bin_code = "{0:b}".format(int(prefcode))
		kwargs = dict()
		i = 0
		for name in self.pref_names:
			kwargs[name] = bool(bin_code[::-1][i])
			i += 1

		self.__init__(kwargs=kwargs)

	def generate_code(self):
		"""returns int"""
		bin_code = ''
		for name in self.pref_names:
			bin_code += '1' if self.prefs[name] else '0'
			
		return int(bin_code, 2)

	def set(self, what, val):
		self.prefs[what] = val

class Users:
	"""
	```users``` is a dict
			users is {'id': Preferences, ...}
	"""
	users = dict()
	users_filename = 'users.lst'

	def add_user(self, user_id, pref, _write_to_file=True):
		u_pref = Preferences(kwargs=pref)
		if _write_to_file:
			with open(self.users_filename, 'a') as uf:
				print(user_id, u_pref.code, file=uf)

		self.users[user_id] = u_pref


	"_to_remove is a set of str  'user_id'"
	_to_remove = set()
	"_to_modify is a dict   {'user_id': {'what': val, ...}, ...}"
	_to_modify = dict()

	def change(self, remove='', undo_remove='', modify=[]):
		"""
		undo_remove and remove is 'user_id'
		modify is ['user_id', ['what', val]]
		"""
		if remove:
			self._to_remove.add(remove)
		if undo_remove:
			self._to_remove.remove(undo_remove)
		if modify:
			user_id = modify[0]
			if user_id in self._to_modify:
				what = modify[1][0]
				val  = modify[1][1]
				self._to_modify[user_id][what] = val
			self._to_modify[modify[0]] = modify[1]

	def _change(self):
		self._change_list()
		self._change_file()

	def _change_list(self):
		for user in self.users:
			user_id = user
			if user_id in self._to_remove:
				del self.users[user_id]
				pass
			if user_id in self._to_modify:
				u_pref = self.users[user_id]
				new_u_pref = self._to_modify[user_id]

				for key, val in new_u_pref.items():
					self.users[user_id].set(what=key, val=val)

	def _change_file(self):
		with open(self.users_filename, 'w') as uf:
			for user_id, u_pref in self.users.items():
				print(user_id, u_pref.code, file=uf)

	def get_from_file(self):
		with open(self.users_filename, 'r') as uf:
			for line in uf:
				user_id, pref_code = line.split()
				users.add_user(user_id=user_id, pref={'prefcode':pref_code}, _write_to_file=False)

users = Users()
