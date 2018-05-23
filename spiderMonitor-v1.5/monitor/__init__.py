import pymysql
import logging
import time
import apscheduler
from zzh.response import JsonResponse
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.exceptions import HTTPException



pymysql.install_as_MySQLdb()


logger = logging.getLogger('django')

schedul = BackgroundScheduler()


# from zzh.scheduler.sched import reload_runnable_spider_job_execution
# schedul.add_job(reload_runnable_spider_job_execution, 'interval', minutes=1,id='my_scheduler_job')
# # try:
# #     while True:
# #         schedul.start()
# #         time.sleep(2)
# # except (KeyboardInterrupt, SystemExit):
# #     schedul.shutdown()
# #     schedul.start()
# #
# def start_schedler():
#     schedul.start()