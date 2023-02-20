import copy
import os
import pandas as pd
import File_To_Obj
import Utils

# 注意路径，将result_data(北京).txt、result_hun.txt、标识IP集.txt 放入程序sourceData目录，生成的数据在firstData目录下
one_data = pd.read_table(r'sourceData/北京-地标.txt', header=None)
two_data = pd.read_table(r'sourceData/北京/result_qg_4_18_16000-19.txt', header=None)
# 标识IP文件
identity_date = pd.read_table(r'sourceData/标识IP集.txt', header=None)
# 需要补跳的数据
integration1 = pd.read_table(r'sourceData/郑州/郑州轻工业大学_2001-250-4802-6-d9b1-560d-5438-9b5f.txt', header=None)
integration2 = pd.read_table(r'sourceData/原始数据.txt', header=None)

# 十进制IP路径且长度为161的文件名
ten_road_file = '3.csv'
# 此名为数据存入(first&second)Data目录下文件夹的名字/(first&second)Data/湖南/(生成的数据.txt),修改此数据后记得修改two_data路径
dir_name = "广东"
# 相似度阈值
digit = 64


def remove_ip(data):
    """
    移除列表中符合特征的对象
    1.无标识IP
    :param data:
    :return:
    """
    # 逆序移除  重要!!!
    for i in data[::-1]:
        # 标识IP为空
        if i.sign == '':
            data.remove(i)
    # print(1)


def compare_one(compare, data):
    """
    对比并写入文件，注意地址
    :param compare:
    :param data:
    :return:
    """
    hh = '\n'
    if not os.path.exists('./firstData/' + dir_name):
        os.makedirs('./firstData/' + dir_name)
    for i in compare:
        success = []
        for j in data:
            if (i.beg == j.beg) and (i.sign == j.sign):
                success.append(j)
        if len(success) > 0:
            fp = open('./firstData/' + dir_name + '/' + i.name + '.txt', 'w', encoding='utf-8')
            fp.write(i.name + hh)
            fp.write('首跳：' + i.beg + hh)
            fp.write('标识：' + i.sign + hh)
            fp.write('路径: ' + hh)
            for l in range(0, len(i.road)):
                fp.write(str(l + 1) + ' ' + i.road[l] + '  ')
                if l < len(i.delay_min):
                    fp.write(str(i.delay_min[l]) + 'ms')
                    fp.write(str(i.delay_ave[l]) + 'ms')
                    fp.write(str(i.delay_max[l]) + 'ms')
                fp.write(hh)
            fp.write(hh)
            # 打印地标路径
            for k in success:
                fp.write(k.name + hh)
                for h in range(0, len(k.road)):
                    fp.write(str(h + 1) + ' ' + k.road[h] + '  ')
                    if h < len(k.delay_min):
                        fp.write(str(i.delay_min[l]) + 'ms')
                        fp.write(str(i.delay_ave[l]) + 'ms')
                        fp.write(str(i.delay_max[l]) + 'ms')
                    fp.write(hh)
                fp.write(hh)
            fp.write(hh)


def compare_two(compare, data):
    """
    将目标与地标进行对比,返回对比结果[[第一条分别对比][]]
    :param compare:
    :param data:
    :return:
    """
    result = []
    for i in compare:
        success = [i]
        for j in data:
            if (i.beg == j.beg) and (i.sign == j.sign):
                success.append(copy.deepcopy(j))
        if len(success) > 1:
            result.append(success)
    return result


def find_router(data):
    """
    标识出最近路由器到最后一条的路径
    :param data:
    :return:
    """
    for i in data:
        i[0].compare_road = []
        i[0].compare_delay = []
        for j in range(1, len(i)):
            x = compare_ip(i[0].road, i[j].road, i[0].sign)
            i[j].sign_router = x[2]
            i[j].road_router = copy.deepcopy(i[j].road)[len(i[j].road) - x[1] - 1:len(i[j].road) + 1]
            i[j].road_delay = copy.deepcopy(i[j].delay)[len(i[j].delay) - x[1] - 1:len(i[j].delay) + 1]
            i[0].compare_road.append(copy.deepcopy(i[0].road)[len(i[0].road) - x[0] - 1:len(i[0].road) + 1])
            i[0].compare_delay.append(copy.deepcopy(i[0].delay)[len(i[0].delay) - x[0] - 1:len(i[0].delay) + 1])


def compare_ip(target, mark, sign):
    # 倒叙
    target = list(reversed(target))
    mark = list(reversed(mark))
    for i in range(0, mark.index(sign) + 1):
        for j in range(0, target.index(sign) + 1):
            if ("*" in target[j]) or ("*" in mark[i]):
                continue
            if target[j] == mark[i]:
                # 返回其在倒数第几位和最近共同路由器,从0开始
                return [j, i, mark[i]]


def compare_three(data):
    """
    对比最近路由到min(跳数)
    :param data:
    :return:
    """
    for i in data:
        for j in range(1, len(i)):
            flag = 0
            delay = 0
            min_ = min(len(i[0].compare_road[j - 1]), len(i[j].road_router))
            for k in range(0, min_):
                a = i[0].compare_road[j - 1][k]
                b = i[j].road_router[k]
                if ("*" in a) or ("*" in b):
                    continue
                if compare_ip2(a, b, digit):
                    flag += 1
                delay += abs(float(i[0].compare_delay[j - 1][k]) - float(i[j].road_delay[k]))
            i[j].same_road = flag
            i[j].delay_road = delay
            i[j].num_road = min_
            delay1 = [float(x) for x in i[0].compare_delay[j - 1][:min_]]
            delay2 = [float(x) for x in i[j].road_delay[:min_]]
            hstf1 = [list(range(1, min_ + 1)), delay1]
            hstf2 = [list(range(1, min_ + 1)), delay2]
            i[j].hstf = Utils.cal_hstf(hstf1, hstf2)


def compare_ip2(ip1, ip2, position):
    """
    对比IP相似
    :param ip1:
    :param ip2:
    :param position: 位数
    :return:
    """
    ip1 = Utils.tran_comp(ip1)
    ip1 = ip1.replace(":", "")
    ip1 = Utils.tran_sixteen(ip1)
    ip2 = Utils.tran_comp(ip2)
    ip2 = ip2.replace(":", "")
    ip2 = Utils.tran_sixteen(ip2)
    return ip1[:position] == ip2[:position]


def compare_write(data1, data2):
    """
    对比并写入csv文件
    :param data1:
    :param data2:
    :return:
    """
    compare_data = compare_two(data1, data2)
    find_router(compare_data)
    compare_three(compare_data)
    Utils.write_txt(compare_data, dir_name)
    Utils.write_csv(compare_data, ten_road_file)


def integrate_road(data):
    """
    根据传入数据进行对比，路经补齐
    :param data:
    :return:
    """
    # n = len(data)
    for i in data[0]:
        for j in data[1:]:
            for k in j:
                if i.name == k.name:
                    # 补充路径并返回对应数值
                    li = com_ins_road(i.road, k.road)
                    if len(li) != 0:
                        print(i.name)
                        for l in range(0, len(li), 2):
                            i.delay_min[li[l]] = k.delay_min[li[l + 1]]
                            i.delay_max[li[l]] = k.delay_max[li[l + 1]]
                            i.delay_ave[li[l]] = k.delay_ave[li[l + 1]]
    # 将整条路径缺少的补全
    for i in data[1:]:
        for j in i:
            flag = 0
            for k in data[0]:
                if j.name == k.name:
                    flag = 1
            if flag == 0:
                data[0].append(j)


def com_ins_road(data1, data2):
    """
    根据两条路径对比并插入IP
    :param data1:第一条路径
    :param data2:第二条路径
    :return:
    """
    li = []
    flag = 0
    for i in range(0, len(data1)):
        if "*" in data1[i]:
            if i == len(data1) - 1:
                break
            for j in range(0, len(data2)):
                if j == len(data2) - 1:
                    break
                # 判断第一跳是否可以补
                if (i == 0) and ('*' in data1[i]) \
                        and (data1[i + 1] == data2[j + 1]) \
                        and ('*' not in data2[j]) \
                        and (j < 3):
                    flag = 1
                # 判断其他跳
                elif (data1[i - 1] == data2[j - 1]) \
                        and (data1[i + 1] == data2[j + 1]) \
                        and ('*' not in data1[i - 1]) \
                        and ('*' not in data1[i + 1]) \
                        and ('*' not in data2[j]):
                    flag = 1
                if flag == 1:
                    data1[i] = data2[j]
                    print("成功" + ' ' + str(i + 1) + ' ' + str(j + 1) + ' ' + data2[j])
                    li.append(i)
                    li.append(j)
                    flag = 0
    return li


def remove_anonymous(data):
    """
    移除匿名的地址和时延为1
    :param data:
    :return:
    """
    for i in data:
        for j in i.road[::-1]:
            if '*' in j:
                i.road.remove(j)
        for j in i.delay_ave[::-1]:
            if 1 == j:
                i.delay_ave.remove(j)
        for j in i.delay_min[::-1]:
            if 1 == j:
                i.delay_min.remove(j)
        for j in i.delay_max[::-1]:
            if 1 == j:
                i.delay_max.remove(j)
    resort(data)


def resort(data):
    """
    删除匿名节点后进行数据整理
    :param data:
    :return:
    """
    for i in data:
        # 整理首跳信息(西交)
        i.beg = i.road[0]
        # 整理过后的跳数信息
        i.sort_num = len(i.road)


def all_ip_to_csv(data, ip_node_file):
    """
    将IP打标签后输出到excel and 返回节点
    :param ip_node_file: 输出文件
    :param data:
    :return:
    """
    cou = 1
    x = 0
    ip_li = []
    for i in data:
        for j in i.road:
            ip_li.append(j)
    ip_li1 = list(set(ip_li))
    ip_li2 = []
    for i in ip_li1:
        for j in data:
            if i == j.target:
                x = [cou, i, j.name]
                break
            else:
                x = [cou, i, '无']
        cou += 1
        ip_li2.append(x)
    ip = pd.DataFrame(data=ip_li2)
    ip.to_csv(ip_node_file, header=["id:ID", "ip", ":Label"], index=False, encoding='utf-8')
    return ip_li2


def relation_to_csv(data, node, relation_file):
    """
    打印出路径
    :param data:
    :param node:
    :param relation_file:
    :return:
    """
    data_li = []
    nodes = []
    length = []
    cou = 0
    for i in node:
        nodes.append(i[1])
    for i in data:
        length.append(len(i.road))
        for j in i.road:
            data_li.append([nodes.index(j) + 1, 'Relation', ''])
    for i in length:
        for j in range(cou, cou + i - 1):
            data_li[j][2] = data_li[j + 1][0]
            if data_li[j][0] == data_li[j][2]:
                print(data_li[j][1])
        cou += i
    for i in data_li[::-1]:
        if i[2] == '':
            data_li.remove(i)
    data_li1 = [list(t) for t in set(tuple(_) for _ in data_li)]

    relation = pd.DataFrame(data=data_li1)
    relation.to_csv(relation_file, header=[":START_ID", ":TYPE", ":END_ID"], index=False, encoding="utf-8")
    pass


def hxh():
    road = File_To_Obj.sort_one(one_data[0].values, identity_date[0].values)
    remove_anonymous(road)
    zz_ip = []
    zz_id = '2001:da8:2:1::1'
    for i in road:
        if zz_id in i.road:
            print(i.name)
            for j in range(i.road.index(zz_id), len(i.road)):
                zz_ip.append(i.road[j])
    zz_ip = list(set(zz_ip))
    hn_obj = File_To_Obj.sort_one(pd.read_table(r'sourceData/北京-待测.txt', header=None)[0].values,
                                  identity_date[0].values)
    remove_anonymous(hn_obj)
    data = []

    # for i in hn_obj:
    #     li = []
    #     li.append(i.name)
    #     li.append(i.ove)
    #     for j in i.road:
    #         li.append(j)
    #     data.append(li)
    # pass
    for i in hn_obj:
        a = []
        num = 0
        flag = 0
        bs = 0
        zj = 0
        zj_route = 0
        if zz_id in i.road:
            bs = 1
            a.append(1)
        else:
            a.append(0)

        for j in range(0, len(i.road)):
            i.road.reverse()
            if i.road[j] in zz_ip and i.road[j] != zz_id:
                if flag == 0:
                    zj_route = i.road[j]
                flag += 1
                break
        if flag > 0:
            zj = 1
            a.append(1)
        else:
            a.append(0)
        if bs == 1:
            num = i.road.index(zz_id) + 1
        else:
            if zj == 1:
                num = i.road.index(zj_route) + 1
            else:
                num = len(i.road)
        # a.append(i.name)
        a.append(Utils.tran_comp(i.target)[:14])
        i.delay_min.reverse()
        for k in range(0, num):
            a.append(i.delay_min[k])
        data.append(a)
    # for i in data[::-1]:
    #     if (i[0] != 0) and (i[0] != 1):
    #         data.remove(i)
    # node_li = all_ip_to_csv(road0, 'outData/node4.csv')
    # relation_to_csv(road0, node_li, 'outData/relation4.csv')
    pd.DataFrame(data=data).to_csv('bj待测.csv')


def zsc():
    hn_file = pd.read_table(r'sourceData/郑州/hn高校.txt', header=None)
    # print(hn_file)
    hn_gx = []
    for i in hn_file[0].values:
        hn_gx.append(i)
    all_file = pd.read_table(r'sourceData/郑州/郑州轻工业大学_2001-250-4802-6-d9b1-560d-5438-9b5f.txt',
                             header=None)[0].values
    hh = '\n'
    fp = open('hn.txt', 'w', encoding='utf-8')
    i = 0
    res = []
    while i < len(all_file):
        if (all_file[i] in hn_gx) and (('学' in all_file[i]) or ('院' in all_file[i])):
            print(all_file[i])
            fp.write(all_file[i] + hh)
            li = [all_file[i]]
            j = i + 2
            while ('学' not in all_file[j]) and ('院' not in all_file[j]):
                if '路由' in all_file[j]:
                    j += 1
                all_file[j] = all_file[j].replace('ms', '')
                s = all_file[j].rfind('  ')
                for k in all_file[j][:s].split():
                    li.append(k)
                fp.write(all_file[j][:s] + hh)
                j += 1
            res.append(li)
        i += 1
    pd.DataFrame(data=res).to_excel('hn.xlsx')


if __name__ == '__main__':
    # 对比所需数据
    # landmark_obj = File_To_Obj.sort_one(one_data[0].values)
    # test_obj = File_To_Obj.sort_one(two_data[0].values)

    # 首次对比并写入数据
    # compare_one(test_obj, landmark_obj)

    # 将存入文件data目录的数据单独存下来
    # compare_data1 = copy.deepcopy(test_obj)
    # all_data1 = copy.deepcopy(landmark_obj)

    # 二次对比并按需输出数据
    # compare_write(test_obj, landmark_obj)

    # 整合数据
    # road1 = File_To_Obj.sort_one(integration1[0].values, identity_date[0].values)
    # road2 = File_To_Obj.sort_one(integration2[0].values, identity_date[0].values)
    # roads = [road1, road2]
    # integrate_road(roads)
    # road0 = roads[0]
    # remove_anonymous(road0)
    # node_li = all_ip_to_csv(road0, 'outData/node4.csv')
    # relation_to_csv(road0, node_li, 'outData/relation4.csv')
    # zsc()
    bj = File_To_Obj.sort_base(pd.read_table(r'sourceData/北京/result_qg_4_18_16000-19.txt', header=None)[0].values)
    hn_colleges = pd.read_table(r'C:\Users\董麒麟\Documents\Python\IPv6Data\sourceData\郑州\hn高校.txt', header=None)[
        0].values
    hn = []
    for i in bj:
        for j in hn_colleges:
            if j in i.name:
                hn.append(i)
    for i in bj[:-1]:
        if i.name.isdigit():
            bj.remove(i)
    result = []
    for i in hn:
        tmp = [i.name]
        for j in i.road:
            tmp.append(Utils.sixteen_two(j)[:48])
        for j in i.delay_min:
            tmp.append(j)
        result.append(tmp)
    remove_anonymous(bj)
    pd.DataFrame(data=result).to_excel('IPv6河南（比赛）.xlsx')
    pass
