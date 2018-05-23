#-*- coding:utf-8 -*-
from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger


def pageT(request,list,page_num):
    # li = eval('')
    paginator = Paginator(list, page_num)
    # 从前端获取当前的页码数,默认为1
    page = request.GET.get('page', 1)
    # 把当前的页码数转换成整数类型
    currentPage = int(page)
    try:
        print(page)
        avalidItemList = paginator.page(page)  # 获取当前页码的记录
        return avalidItemList
    except PageNotAnInteger:
        avalidItemList = paginator.page(1)  # 如果用户输入的页码不是整数时,显示第1页的内容
        return avalidItemList
    except EmptyPage:
        avalidItemList = paginator.page(paginator.num_pages)  # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        return avalidItemList