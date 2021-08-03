def arista():
    start = "^! Command: show running-config$"
    stop = "^end$"
    return start, stop


def brocade():
    start = "^Current configuration:$"
    stop = "^end$"
    return start, stop

def cisco():
    #start = "^version 12.2$"
    start = "^Building configuration...$"
    stop = "^end$"
    return start, stop


def mikrotik():
    start = "^\/interface ethernet$"
    stop = "^\[Admin_KE@"
    return start, stop


def redback():
    start = "^Current configuration:$"
    stop = "^end$"
    return start, stop

def juniper():
    start = "^show configuration \| display set \| no-more $"
    stop = "^{master:[0-1]}$"
    return start,stop

def fs():
    start = "^Building configuration...$"
    stop = "^end$"
    return start,stop

