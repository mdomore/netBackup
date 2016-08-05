ret_char = '\r'


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
    return session


def redback(session, user, password):
    session.expect('login: $')
    session.send(user + ret_char)
    session.expect('Password: $')
    session.send(password + ret_char)
    session.expect('#$')
    return session

