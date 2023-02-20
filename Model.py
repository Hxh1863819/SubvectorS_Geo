class Line:
    def __init__(self, num, name, target, beg, ove, sign, road, delay_min, delay_max, delay_ave):
        # 跳数
        self.num = num
        # 地址名
        self.name = name
        # 目标
        self.target = target
        # 开始地址
        self.beg = beg
        # 结束地址
        self.ove = ove
        # 标识IP
        self.sign = sign
        # 路径
        self.road = road
        # 最小时延
        self.delay_min = delay_min
        # 最大时延
        self.delay_max = delay_max
        # 平均时延
        self.delay_ave = delay_ave


class IdentLine:
    def __init__(self, name, ip, fit):
        # 名字
        self.name = name
        # 标识IP
        self.ip = ip
        # 符合标识IP的地址对象
        self.fit = fit


class IP:
    def __init__(self, num, ip, name):
        # 序号
        self.num = num
        # 地址
        self.ip = ip
        # 地址名
        self.name = name


class Relation:
    def __init__(self, sign, ip, next_sign):
        self.sign = sign
        self.ip = ip
        self.next_sign = next_sign
