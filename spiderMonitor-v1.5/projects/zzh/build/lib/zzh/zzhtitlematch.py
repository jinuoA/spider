# -*- coding: utf-8 -*-

#import titleconfig
from . import titleconfig
#加载配置字典
dic1 = titleconfig.dic1
dic2 = titleconfig.dic2
dic3 = titleconfig.dic3

dic4 = titleconfig.dic4
dic5 = titleconfig.dic5
dic6 = titleconfig.dic6
dic7 = titleconfig.dic7
dic8 = titleconfig.dic8
dic9 = titleconfig.dic9
dic10 = titleconfig.dic10
dic11 = titleconfig.dic11


def jieba_backward_method_1(title):  # 如果匹配到了，那就 false，匹配字典 8,双词匹配
    for pattern in dic8:
        if pattern[0] in title:
            if pattern[1] in title.split(pattern[0])[1]:
                return False
            else:
                pass
        else:
            pass
    return True


def jieba_backward_method_2(title):  # 如果匹配到了，那就false， 匹配字典9，不可连接的双词匹配
    for pattern in dic9:
        if pattern[0] in title and pattern[1] in title.split(pattern[0])[1]:
            if pattern[0]+pattern[1] in title:
                return True  # 连续都在标题中，返回 True
            else:
                return False  # 连续不在标题中，返回False，说明不是想要的标题
        else:
            pass
    return True  # 指没匹配到


def jieba_backward_method_3(title):  # 如果匹配到了，那就 false，匹配字典 11
    for pattern in dic11:
        if pattern[0] in title:
            if pattern[1] in title.split(pattern[0])[1]:
                end_string = title.split(pattern[0])[1]
                if pattern[2] in end_string.split(pattern[1])[1]:
                    return False
                else:
                    pass
            else:
                pass
        else:
            pass
    return True
########################################################################################################################
#AC多模匹配

# 结点类
class node:
    def __init__(self, name):
        self.name = name  # 结点值
        self.fail = None  # Fail指针
        self.tail = 0  # 尾标志：标志为 i 表示第 i 个模式串串尾
        self.child = []  # 子结点
        self.childvalue = []  # 子结点的值

    def __repr__(self):
        return 'name: %s, fail:%s,tail: %s, child:%s,childvalue: %s' % (self.name, self.fail, self.tail,
                                                                      self.child, self.childvalue)
# AC自动机类
class acmation:
    def __init__(self):
        self.root = node("")  # 初始化根结点
        self.count = 0  # 模式串个数
    # 第一步：模式串建树
    def insert(self, strkey):
        self.count += 1  # 插入模式串，模式串数量加一
        p = self.root
        for i in strkey:
            if i not in p.childvalue:  # 若字符不存在，添加子结点
                child = node(i)
                p.child.append(child)
                p.childvalue.append(i)
                p = child
            else:  # 否则，转到子结点
                p = p.child[p.childvalue.index(i)]
        p.tail = self.count  # 修改尾标志

    # 第二步：修改Fail指针
    def ac_automation(self):
        queuelist = [self.root]  # 用列表代替队列
        while len(queuelist):  # BFS遍历字典树
            temp = queuelist[0]
            queuelist.remove(temp)  # 取出队首元素
            for i in temp.child:
                if temp == self.root:  # 根的子结点Fail指向根自己
                    i.fail = self.root
                else:
                    p = temp.fail  # 转到Fail指针
                    while p:
                        if i.name in p.childvalue:  # 若结点值在该结点的子结点中，则将Fail指向该结点的对应子结点
                            i.fail = p.child[p.childvalue.index(i.name)]
                            break
                        p = p.fail  # 否则，转到Fail指针继续回溯
                    if not p:  # 若p==None，表示当前结点值在之前都没出现过，则其Fail指向根结点
                        i.fail = self.root
                queuelist.append(i)  # 将当前结点的所有子结点加到队列中

    # 第三步：模式匹配
    def runkmp(self, strmode):
        p = self.root
        cnt = {}  # 使用字典记录成功匹配的状态
        cnList = []
        for i in strmode:  # 遍历目标串
            while i not in p.childvalue and p is not self.root:
                p = p.fail
            if i in p.childvalue:  # 若找到匹配成功的字符结点，则指向那个结点，否则指向根结点
                p = p.child[p.childvalue.index(i)]
            else:
                p = self.root
            temp = p
            while temp is not self.root:
                if temp.tail:  # 尾标志为0不处理
                    #print temp.name
                    if temp.tail not in cnt:
                        cnList.append(temp.tail)
                        cnt.setdefault(temp.tail)
                        cnt[temp.tail] = 1
                    else:
                        cnt[temp.tail] += 1
                temp = temp.fail
        if len(cnList) > 0:
            return 1
        else:
            return 0


def ACSliceMethod(strmode):  # 对字典123的处理识别
    oneMation = acmation()
    for strkey in dic1:
        oneMation.insert(strkey)
    oneMation.ac_automation()
    oneMatch = oneMation.runkmp(strmode)

    twoMation = acmation()
    for strkey in dic2:
        twoMation.insert(strkey)
    twoMation.ac_automation()
    twoMatch = twoMation.runkmp(strmode)

    threeMation = acmation()
    for strkey in dic3:
        threeMation.insert(strkey)
    threeMation.ac_automation()
    threeMatch = threeMation.runkmp(strmode)
    # print oneMatch,twoMatch,threeMatch
    if oneMatch + twoMatch + threeMatch >= 2:
        return True
    else:
        return False


def ACMatchMethod(strmode):  # 对字典 4567 的处理
    oneMation = acmation()
    for strkey in dic4:
        oneMation.insert(strkey)
    oneMation.ac_automation()
    oneMatch = oneMation.runkmp(strmode)
    if oneMatch:
        return True
    twoMation = acmation()
    for strkey in dic5:
        twoMation.insert(strkey)
    twoMation.ac_automation()
    twoMatch = twoMation.runkmp(strmode)
    if twoMatch:
        return True

    threeMation = acmation()
    for strkey in dic6:
        threeMation.insert(strkey)
    threeMation.ac_automation()
    threeMatch = threeMation.runkmp(strmode)
    if threeMatch:
        return True
    fourMation = acmation()
    for strkey in dic7:
        fourMation.insert(strkey)
    fourMation.ac_automation()
    fourMatch = fourMation.runkmp(strmode)
    if fourMatch:
        return True
    else:
        return False


def ac_backward_method(strmode):  # 得到反向排查词汇,如果没有匹配到，返回True
    oneMation = acmation()
    for strkey in dic10:
        oneMation.insert(strkey)
    oneMation.ac_automation()
    oneMatch = oneMation.runkmp(strmode)
    if not oneMatch:
        return True
    else:
        return False


def TitleMatchMethod(strmode):
    # oneResult = ACSliceMethod(strmode)  # 正向1
    # twoResult = ACMatchMethod(strmode)  # 正向2
    # backward_result = ac_backward_method(strmode)  # 反向单个词组匹配
    # jieba_backward_result_1 = jieba_backward_method_1(strmode)  # 反向多词组匹配 1， 2词连接不可选
    # jieba_backward_result_2 = jieba_backward_method_2(strmode)  # 反向多词组匹配 2， 2连接可选
    # jieba_backward_result_3 = jieba_backward_method_3(strmode)  # 反向多词组匹配 3， 3词连接可选
    if ACSliceMethod(strmode):  # 正向符合
        if ac_backward_method(strmode) and jieba_backward_method_1(strmode) and jieba_backward_method_2(strmode) and jieba_backward_method_3(strmode):  # 反向符合
            return True
        else:
            return False
    elif ACMatchMethod(strmode):
        if ac_backward_method(strmode) and jieba_backward_method_1(strmode) and jieba_backward_method_2(strmode) and jieba_backward_method_3(strmode):  # 反向符合
            return True
        else:
            return False
    else:
        return False


"""
# 该算法并未使用
def JiebaSliceMethod(title):  # 匹配到字典 123 中的两个
    seg_list = jieba.cut_for_search(title)
    aMatch = list(set(seg_list) & set(dic1))
    bMatch = list(set(seg_list) & set(dic2))
    cMatch = list(set(seg_list) & set(dic3))
    if (len(aMatch) + len(bMatch) + len(cMatch)) >= 2:
        return True
    else:
        return False

# 该算法并未使用
def JiebaMatchMethod(title):  # 匹配到字典 4567 中的一个
    seg_list = jieba.cut_for_search(title)
    aMatch = list(set(seg_list) & set(dic4))
    bMatch = list(set(seg_list) & set(dic5))
    cMatch = list(set(seg_list) & set(dic6))
    dMatch = list(set(seg_list) & set(dic7))
    if len(aMatch) or len(bMatch) or len(cMatch) or len(dMatch):
        return True
    else:
        return False
"""