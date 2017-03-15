def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]


def mean(values):
    return sum(values) / len(values)


def sign(value):
    if value <  0: return -1
    if value == 0: return  0
    if value >  0: return  1
