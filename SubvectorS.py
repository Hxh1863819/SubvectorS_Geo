def vector(li_):
    all_li = []
    for i in li_:
        i.reverse()
        for j in range(2, len(i) + 1):
            all_li.append(i[:j])
    return all_li


if __name__ == '__main__':
    li01 = [[1, 2, 3], [5, 4, 3, 2, 1]]
    li02 = vector(li01)
    print(li02)
