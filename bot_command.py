from bot_sender import sender

class MessageGenerator:
	@staticmethod
	def by_launch_id(id):
		pass

	@staticmethod
	def by_agency_id(id):
		pass

	@staticmethod
	def by_rocket_id(id):
		pass

	@staticmethod
	def by_mission_id(id):
		pass

	@staticmethod
	def by_stat_of_launch(id):
		pass


def CommandID(user_id, id):
	sender.Send(user_id, MessageGenerator.by_launch_id(id))

def CommandAG(user_id, id):
	sender.Send(user_id, MessageGenerator.by_agency_id(id))

def CommandRO(user_id, id):
	sender.Send(user_id, MessageGenerator.by_rocket_id(id))

def CommandMI(user_id, id):
	sender.Send(user_id, MessageGenerator.by_mission_id(id))

def CommandSTAT(user_id, id):
	sender.Send(user_id, MessageGenerator.by_stat_of_launch(id))

def Command(user_id, com):
	'''
	com can be:
			id :  'id_222'
			agency : 'ag_12123'
			rocket : 'ro_2232'
			status : 'stat_2323' # check if ok
			mission : 'mi_3232'
	'''
	key = com[:2]
	if 'id' == key:
		CommandID(user_id, com[3:])
	elif 'ag' == key:
		CommandAG(user_id, com[3:])
	elif 'ro' == key:
		CommandRO(user_id, com[3:])
	elif 'mi' == key:
		CommandMI(user_id, com[3:])
	elif 'stat' == com[5:]:
		CommandSTAT(user_id, com[6:])
	else:
		sender.Send(user_id, 'Command is wrong!')
