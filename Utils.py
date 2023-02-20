import operator
import numpy as np
import os
import pandas as pd

# IPv6 16进制转2进制字典
dic = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111',
       '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'}


def tran_comp(sim_ip):
    """
    简略地址转换为详细地址(16进制)
    :param sim_ip:
    :return:
    """
    if sim_ip == "::":
        return "0000:0000:0000:0000:0000:0000:0000:0000"
    ip_list = ["0000", "0000", "0000", "0000", "0000", "0000", "0000", "0000"]
    if sim_ip.startswith("::"):
        tmp_list = sim_ip.split(":")
        for i in range(0, len(tmp_list)):
            ip_list[i + 8 - len(tmp_list)] = ("0000" + tmp_list[i])[-4:]
    elif sim_ip.endswith("::"):
        tmp_list = sim_ip.split(":")
        for i in range(0, len(tmp_list)):
            ip_list[i] = ("0000" + tmp_list[i])[-4:]
    elif "::" not in sim_ip:
        tmp_list = sim_ip.split(":")
        for i in range(0, len(tmp_list)):
            ip_list[i] = ("0000" + tmp_list[i])[-4:]
    else:
        tmp_list = sim_ip.split("::")
        tmp_list0 = tmp_list[0].split(":")
        for i in range(0, len(tmp_list0)):
            ip_list[i] = ("0000" + tmp_list0[i])[-4:]
        tmp_list1 = tmp_list[1].split(":")
        for i in range(0, len(tmp_list1)):
            ip_list[i + 8 - len(tmp_list1)] = ("0000" + tmp_list1[i])[-4:]
    return ":".join(ip_list)


def tran_sixteen(data):
    """
    十六进制转二进制核心
    :param data:
    :return:
    """
    result = ""
    for i in data:
        result += dic.get(i)
    return result


def sixteen_two(ip):
    """
    十六进制转二进制
    :param ip:
    :return:
    """
    if '*' in ip:
        return "* * *"
    data = tran_comp(ip)
    data = data.replace(":", "")
    return tran_sixteen(data)


def cal_hstf(a, b):
    """
    计算hstf距离
    传入为
    A=[[1,3,3],
      [4,5,6]]
    B=[[1,2,3],
      [4,8,7]]
    :param a:
    :param b:
    :return:
    """
    a_size = [len(a), len(a[0])]
    b_size = [len(b), len(b[0])]
    if a_size[1] != b_size[1]:
        print('The dimensions of points in the two sets are not equal')
    fhd = 0
    for i in range(a_size[0]):
        min_dist = float("inf")
        for j in range(b_size[0]):
            temp_dist = np.linalg.norm(list(map(operator.sub, a[i], b[j])))
            if temp_dist < min_dist:
                min_dist = temp_dist
        fhd = fhd + min_dist
    fhd = fhd / a_size[0]
    rhd = 0
    for j in range(b_size[0]):
        min_dist = float("inf")
        for i in range(a_size[0]):
            temp_dist = np.linalg.norm(list(map(operator.sub, a[i], b[j])))
            if temp_dist < min_dist:
                min_dist = temp_dist
        rhd = rhd + min_dist
    rhd = rhd / b_size[0]
    mhd = max(fhd, rhd)
    return mhd

def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def write_txt(data, dir_name):
    """
    写入dir_name文件夹
    :param data:
    :param dir_name:
    :return:
    """
    hh = '\n'
    if not os.path.exists('./secondData/' + dir_name):
        os.makedirs('./secondData/' + dir_name)
    for i in data:
        result = ""
        # 存储前缀相似值
        per_sim = []
        # 存储hstf
        hstf_sim = []
        # 存储地标路径名
        road_name = []
        fp = open('./secondData/' + dir_name + '/' + i[0].name + '.txt', 'w', encoding='utf-8')
        fp.write(i[0].target + hh)
        for j in range(1, len(i)):
            fp.write(i[j].name + ' ')
            road_name.append(i[j].name)
            fp.write('前缀相似度:' + "(" + str(float(i[j].num_road) / float(len(i[j].road_router))) + ')' + ' ')
            per_sim.append(float(i[j].num_road) / float(len(i[j].road_router)))
            fp.write('时延相似度' + "(" + str(i[j].hstf) + ")" + hh)
            hstf_sim.append(i[j].hstf)
        a = hstf_sim.index(min(hstf_sim))
        b = per_sim.index(max(per_sim))
        if a == b:
            result = road_name[a]
            fp.write('定位结果:' + road_name[a] + hh)
        else:
            result = road_name[a] + '|' + road_name[b]
            fp.write('定位结果:' + road_name[a] + ',' + road_name[b] + hh)
        i[0].result = result


def write_csv(data, file_name):
    """
    输出名为file_name的10进制csv文件，且截取长度为161 十进制截取
    :param file_name:
    :param data:
    :return:
    """
    # count = 0
    sum_ = []
    for i in data:
        x = [i[0].name]
        for j in i[0].road:
            if '*' in j:
                continue
            for k in tran_comp(j).split(":"):
                a = int(k, 16)
                x.append(a)
        # if len(x) >= 21:
        #     count+=1
        # 截取长度
        while len(x) < 161:
            for k in tran_comp("::0").split(":"):
                a = int(k, 16)
                x.append(a)
        x.append(i[0].result)
        if len(x) == 162:
            sum_.append(x)
    # print(sum_)
    data = pd.DataFrame(data=sum_)
    # print(data)
    data.to_csv(file_name)
