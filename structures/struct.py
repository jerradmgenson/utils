from collections import namedtuple


def struct(name, items):
    struct_class = namedtuple(name, [item[0] for item in items])
    struct_object = struct_class(*[item[1] for item in items])
    return struct_object
