from bot_logging import scheduler, logger
from bot_interface import interface
from bot_sender import sender

class LastWeek:
	'a table of msgs to be send as needed'
	table = []

	def add_event(self, event):
		'adds event and sets schedular to remove it in 8 days'
		self.table.append(interface.generate_msg(event, past=True))
		scheduler.add_job(self.remove_first,
			trigger='date', run_date=event['when'].shift(days=+8).datetime)

	def remove_first(self):
		del self.table[0]

	def get_all(self):
		return self.table

lastweek = LastWeek()