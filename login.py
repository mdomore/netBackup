ret_char = '\r'

def juniper(session, user, password):
    return session

def arista(session, user, password):
    return session


def brocade(session, user, password):
    session.expect('Login Name: $')
    session.send(user + ret_char)
    session.expect('Password: $')
    session.send(password + ret_char)
    session.expect('#$')
    return session


def cisco(session, user, password):
    session.expect("Username: $")
    session.send(user + ret_char)
    session.expect('Password: $')
    session.send(password + ret_char)
    session.expect('#$')
    return session


def mikrotik(session, user, password):
    session.expect('Login: $')
    session.send(user + ret_char)
    session.expect('Password: $')
    session.send(password + ret_char)
    session.expect('> $')
    return session


def redback(session, user, password):
    session.expect('login: $')
    session.send(user + ret_char)
    session.expect('Password: $')
    session.send(password + ret_char)
    session.expect('#$')
    return session


