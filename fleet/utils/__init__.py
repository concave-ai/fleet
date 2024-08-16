def unique_list(l):
    s = set()
    res = []
    for i in l:
        if i not in s:
            res.append(i)
            s.add(i)
    return res