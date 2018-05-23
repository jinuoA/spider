from django.contrib import admin

# Register your models here.
from .models import  Project, Monitor,ProjectRuler,Scheduler,Spider,Node,Task_url,Item_monitor,Fail_url_detail, \
    Spider_url_monitor,SpiderTemplates,Queue_url_monitor


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'port', 'created_at', 'updated_at')

#
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'configurable', 'built_at', 'generated_at')
#
#
# class MonitorAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'project', 'created_at', 'updated_at')
#
#
# class ProjectRulerAdmin(admin.ModelAdmin):
#     list_display = ('','','','',)
#
# class SchedulerAdmin(admin.ModelAdmin):
#     list_display = ('schedule_name','schedule_desc','schedule_time','create_time',)

# class SpiderAdmin(admin.ModelAdmin):
#     list_display = ('','','','',)
#
# class NodeAdmin(admin.ModelAdmin):
#     list_display = ('','','','',)


admin.site.register(Project)
admin.site.register(Monitor)
admin.site.register(ProjectRuler)
admin.site.register(Scheduler)
admin.site.register(Spider)
admin.site.register(Node)
admin.site.register(Fail_url_detail)
admin.site.register(Queue_url_monitor)
admin.site.register(SpiderTemplates)
admin.site.register(Spider_url_monitor)
admin.site.register(Item_monitor)
admin.site.register(Task_url)


