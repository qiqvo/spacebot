import logging
import arrow

import apscheduler.jobstores.base
from apscheduler.schedulers.background import BackgroundScheduler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


scheduler = BackgroundScheduler()