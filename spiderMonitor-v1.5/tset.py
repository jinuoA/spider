# from apscheduler.schedulers.background import BackgroundScheduler
#
# sche = BackgroundScheduler()
# def test():
#     print('-------------')
#
#
#
# # def demo():
# #     sche.add_job(test,'cron',day_of_week='mon-fri',month=4,hour='0-24',minute='0-60',second='*/30',id='a')
# #     print('**************')
# sche.add_job(test,'interval', minutes=1, id='my_scheduler_job')
#
# sche.start()


"""
import time
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
def my_job():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

def demo():
    sched.add_job(my_job,trigger='cron',day_of_week='mon-fri',month=4,day='*',hour='0-24',minute='0-60',second=0,id='123',misfire_grace_time=60 * 60,coalesce=True)
    # print('**************')
    # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    sched.remove_job(job_id='123')


sched.add_job(my_job,trigger='cron',day_of_week='mon-fri',month=4,day='*',hour='0-24',minute=0,second=0,id='1234',misfire_grace_time=60 * 60,coalesce=True)
# sched.add_job(demo, 'interval', seconds=10,id='b')

sched.start()

"""
for i in range(1,10):
    print(i,"xxxxxxxxxxxxxxxxxx")

a = 1
b = 2

print(a+b-1)



