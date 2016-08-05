def arista():
    return start, stop


def brocade():
    start = "^Current configuration:$"
    stop = "^end$"
    return start, stop


def cisco():
    return start, stop


def redback():
    start = "^Current configuration:$"
    stop = "^end$"
    return start, stop

