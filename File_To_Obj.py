import Model
import numpy as np

from Utils import is_chinese


def sort_one(data1, data2):
    # 判断是win还是linux
    if '路由' in data1[1]:
        obj = read_from_win_txt(data1)
    else:
        obj = read_from_linux_txt(data1)
    identity_obj = sort_identity(data2)
    add_identity(obj, identity_obj)
    # remove_ip(obj)
    return obj


def sort_base(data):
    """
    不需要打标识IP的整理
    :param data:
    :return:
    """
    if '路由' in data[1]:
        obj = read_from_win_txt(data)
    else:
        obj = read_from_linux_txt(data)
    return obj


def read_from_linux_txt(data):
    """
    从Linux_Txt文件中读入数据，并整理
    :param data:Panda读入的Txt文件
    :return:
    """
    li = []
    str_ = ""
    for i in data:
        # print(type(i))
        if is_chinese(i) or i.isdigit():
            # 判断是否要舍弃(先不舍弃)
            if (len(str_) > 10):  # and ("30  * * *" not in str_):
                li.append(str_)
            str_ = i + ';'
        elif not is_chinese(i):
            str_ += i + ';'
    # 将最后一条加入到列表
    if len(str_) > 10:  # and ("30  * * *" not in str_):
        li.append(str_)
    return store_linux(li)


def store_linux(data):
    """
    整理后的数据 *筛选后* 存入一个个对象
    :param data:
    :return:
    """
    obj = []
    for i in data:
        flag = 0
        beg = ""
        road = []
        delay_min = []
        delay_max = []
        delay_ave = []
        part = i.split(";")
        for j in range(2, len(part) - 1):
            # 设置首跳地址
            if part[2].find("(") != -1:
                beg = part[2][part[2].find("(") + 1:part[2].find(")")]
            else:
                beg = "* * *"
            # 设置路径,如果为匿名路由器则路径设置为* * *
            x = part[j][part[j].find("(") + 1:part[j].find(")")]
            if "  * * *" in part[j]:
                road.append("* * *")
            elif x in road:
                flag = 1
            else:
                road.append(x)

            # 设置时延,如果为匿名路由器则设置为1
            if "  * * *" in part[j]:
                delay_min.append(1)
                delay_max.append(1)
                delay_ave.append(1)
            elif "!H" in part[j]:
                # 舍弃!H
                flag = 1
            else:
                li = delay_3_linux(part[j])
                delay_min.append(li[0])
                delay_max.append(li[1])
                delay_ave.append(li[2])

        # 筛选规则

        # 路径包含此三个IP舍弃
        if ("2001:da8:257:0:101:4:9:8022" in road) or ("2001:da8:257:0:101:4:9:8032" in road) \
                or ("2001:da8:2:101::102" in road):
            flag = 1
        # 若最后一跳为匿名舍弃
        if (len(road) == 30) and ("* * *" in road[29]):
            flag = 1

        target = part[1][part[1].find("(") + 1:part[1].find(")")]
        # 未达到目标地址舍弃
        if target != road[len(road) - 1]:
            flag = 1
        if flag == 1:
            continue
        # 对象的构造方法
        x = Model.Line(part[len(part) - 2][0:2],
                       part[0],
                       target,
                       beg,
                       part[len(part) - 2][part[len(part) - 2].find("(") + 1:part[len(part) - 2].find(")")],
                       "",
                       road,
                       delay_min,
                       delay_max,
                       delay_ave)
        obj.append(x)
    # 返回整理好的路径对象列表
    return obj


def read_from_win_txt(data):
    data = org_data(data)
    li = []
    str_ = ""
    for i in data:
        # print(type(i))
        if "跟踪完成" in i:
            li.append(str_)
            str_ = ''
        else:
            str_ += i + ';'
    # 将最后一条加入到列表
    if len(str_) > 10:
        li.append(str_)
    return store_win(li)


def org_data(data):
    """
    将单句'通过最多 30 个跃点跟踪'进行拼接并删除下一句
    :param data:
    :return:
    """
    data = data.tolist()
    for i in range(0, len(data)):
        if '通过最多 30 个跃点跟踪' == data[i]:
            data[i + 1] = data[i] + data[i + 1]
    for i in data[::-1]:
        if '通过最多 30 个跃点跟踪' == i:
            data.remove(i)
    return data


def delay_3_win(param):
    """
    求出该字符串中最小时延,最大时延，平均时延
    :param param:
    :return:
    """

    # if ('毫秒' in param) and ('ms' not in param):
    #     param = '1'
    # elif '毫秒' in param:
    #     param = param[param.find("ms") - 5:param.rfind("ms ")] + ' 1'
    # elif 'ms' in param:
    #     param = param[param.find("ms") - 5:param.rfind("ms ")]
    param = param.replace('<1 毫秒', '1 ms')
    param = param[param.find("ms") - 5:param.rfind("ms ")]
    param = param.replace(" *", "")
    param = param.replace(" ms", "")
    delay_li = param.split("  ")
    while '' in delay_li:
        delay_li.remove('')
    delay_li = list(map(float, delay_li))
    li = [min(delay_li), max(delay_li), np.mean(delay_li)]
    return li


def store_win(data):
    """
    整理后的数据 *筛选后* 存入一个个对象
    :param data:
    :return:
    """
    obj = []
    for i in data:
        flag = 0
        beg = ""
        road = []
        delay_min = []
        delay_max = []
        delay_ave = []
        part = i.split(";")
        for j in range(2, len(part) - 1):
            # 设置首跳地址
            if 'ms' in part[2]:
                beg = part[2][part[2].rfind("s") + 3:len(part[2])]
            elif '毫秒' in part[2]:
                beg = part[2][part[2].rfind(' ')+1:]
            else:
                beg = "* * *"
            # 设置路径,如果为匿名路由器则路径设置为* * *
            if '[' in part[j]:
                x = part[j][part[j].find("[") + 1:part[j].find("]")]
            else:
                x = part[j][part[j].rfind(' ')+1:]

            if "请求超时" in part[j]:
                road.append("* * *")
            # 回环路由
            elif x in road:
                flag = 1
            elif '无法访问' in part[j]:
                continue
            else:
                road.append(x)

            # 设置时延,如果为匿名路由器则设置为1
            if "请求超时" in part[j]:
                delay_min.append(1)
                delay_max.append(1)
                delay_ave.append(1)
            elif "!H" in part[j]:
                # 舍弃!H
                flag = 1
            else:
                li = delay_3_win(part[j])
                delay_min.append(li[0])
                delay_max.append(li[1])
                delay_ave.append(li[2])

        # 筛选规则

        # 路径包含此三个IP舍弃
        if ("2001:da8:257:0:101:4:9:8022" in road) or ("2001:da8:257:0:101:4:9:8032" in road) \
                or ("2001:da8:2:101::102" in road):
            flag = 1
        # 若最后一跳为匿名舍弃
        if (len(road) == 30) and ("* * *" in road[29]):
            flag = 1
        if '[' in part[1]:
            target = part[1][part[1].find("[") + 1:part[1].find("]")]
        else:
            target = part[1][part[1].find("到") + 2:part[1].find("的") - 1]
        # 未达到目标地址舍弃
        # 待改 郑州黄河护理职业学院影响 删除
        if (len(road) != 0) and (target != road[len(road) - 1]):
            flag = 1
        if flag == 1:
            continue
        # 对象的构造方法
        x = Model.Line(part[len(part) - 2][0:2],
                       part[0],
                       target,
                       beg,
                       part[len(part) - 2][part[len(part) - 2].find("(") + 1:part[len(part) - 2].find(")")],
                       "",
                       road,
                       delay_min,
                       delay_max,
                       delay_ave)
        obj.append(x)
    # 返回整理好的路径对象列表
    return obj


def sort_identity(data):
    """
    读入标识路径，并存入一个个标识对象
    :param data:
    :return:
    """
    identity = []

    for i in data:
        str1 = i[0:2]
        str2 = i[3:20]
        # 标识对象构造方法
        x = Model.IdentLine(str1, str2, [])
        identity.append(x)
    # 返回整理好的标识对象列表
    return identity


def add_identity(data, identity):
    """
    标识数据(添加对象的标识IP)
    :param data:需要补充数据
    :param identity:标识IP集
    :return:
    """
    for i in identity:
        for obj in data:
            road = list(reversed(obj.road))
            # print(road)
            # print(obj.name)
            for x in road:
                if i.ip == x:
                    obj.sign = x
                    break


def delay_3_linux(part):
    """
    求出该字符串中最小时延,最大时延，平均时延
    :param part:
    :return:
    """
    part = part[part.rfind(")") + 3:len(part)]
    part = part.replace(" ms", "")
    part = part.replace(" *", "")
    part = part.replace(" !X", "")
    part = part.replace(" !N", "")
    delay_li = part.split("  ")
    delay_li = list(map(float, delay_li))
    li = [min(delay_li), max(delay_li), np.mean(delay_li)]
    return li
