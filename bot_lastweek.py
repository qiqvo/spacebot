import requests
import arrow

from bot_logging import scheduler, logger
from bot_interface import interface
from bot_sender import sender

class LastWeek:
	'a table of msgs to be send as needed'
	table = []

	def add_event(self, event):
		'adds event and sets schedular to remove it in 22 days'
		self.table.append(interface.generate_msg(event, past=True))
		# scheduler.add_job(self.remove_first,
		# 	trigger='date', run_date=event['when'].shift(days=+22).datetime)

	def remove_first(self):
		del self.table[0]

	def update(self):
		self.table.clear()

		from bot_base import create_event
		logger.info("Picking launches in LASTWEEK...")
		start_date = arrow.utcnow().shift(days=-21).format('YYYY-MM-DD')
		end_date = arrow.utcnow().format('YYYY-MM-DD')
		r = requests.get('https://launchlibrary.net/1.2/launch?startdate=' + start_date +
					 '&enddate=' + end_date + '&mode=verbose')
		if r.status_code == 200:
			raw = r.json()['launches']
			for item in raw:
				event = create_event(item)
				self.add_event(event)
			if len(raw) < 2:
				logger.error('There is only one or NONE event happend over the last three weeks. Earth might have been occupied.')
		else:
			logger.error('Error: bad request, while picking in LASTWEEK')

	def get_all(self):
		if not self.table:
			self.update()
		return self.table

lastweek = LastWeek()
