import threading
import time
import json
import redis
import datetime
import logging
from zzh.response import JsonResponse


from zzh import schedul
from zzh.models import Scheduler,ProjectRuler
# from zzh.views import CJsonEncoder
from zzh import config


logger = logging.getLogger('django')

class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def SpiderListUrl(scheduler_id):
    data_list = ProjectRuler.objects.filter(scheduler_id=scheduler_id).values()
    data_list = json.dumps(list(data_list), cls=CJsonEncoder)
    data_list = json.loads(data_list)
    for data in data_list:
        # 将字典编码为json字符串
        reminder_str = json.dumps(data)
        # 连接redis并将数据插入redis中
        r = redis.StrictRedis(host=config.redisHost, port=config.redisPort, db=0)
        # r = redis.StrictRedis(host=redis_ip, port=redis_port, db=0)
        print(r.lpush('basescrawler:rules', reminder_str))
    # return JsonResponse(data_list)



def reload_runnable_spider_job_execution():
    '''
    add periodic job to scheduler
    :return:
    '''
    running_job_ids = set([job.id for job in schedul.get_jobs()])
    logger.debug('[running_job_ids] %s' % ','.join(running_job_ids))
    available_job_ids = set()
    # add new job to schedule
    for job_instance in Scheduler.objects.filter(enabled=0, run_type="periodic").all():
        job_id = "spider_job_%s:%s" % (job_instance.id, int(time.mktime(job_instance.create_time.timetuple())))
        available_job_ids.add(job_id)
        if job_id not in running_job_ids:
            try:
                schedul.add_job(SpiderListUrl,
                                  args=(job_instance.id,),
                                  trigger='cron',
                                  id=job_id,
                                  minute=job_instance.cron_minutes,
                                  hour=job_instance.cron_hour,
                                  day=job_instance.cron_day_of_month,
                                  day_of_week=job_instance.cron_day_of_week,
                                  month=job_instance.cron_month,
                                  second=0,
                                  max_instances=999,
                                  misfire_grace_time=60 * 60,
                                  coalesce=True)
            except Exception as e:
                logger.error(
                    '[load_spider_job] failed {} {},may be cron expression format error '.format(job_id, str(e)))
    # remove invalid jobs
    for invalid_job_id in filter(lambda job_id: job_id.startswith("spider_job_"),
                                 running_job_ids.difference(available_job_ids)):
        schedul.remove_job(invalid_job_id)
        logger.info('[drop_spider_job][job_id:%s]' % invalid_job_id)
