import sqlite3


def login(user, password):
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    sql = 'SELECT flag FROM user WHERE username="{0}" AND password="{1}"'
    c.execute(sql.format(user, password))
    res = c.fetchone()
    conn.close()
    if res is None:
        return 'Login failed'
    else:
        return 'Login succeeded, {0}'.format(res[0])


def secure_login(user, password):
    conn = sqlite3.connect('ctf.db')
    c = conn.cursor()
    sql = "SELECT flag FROM user WHERE username=? and password=?"
    c.execute(sql, (user, password))
    res = c.fetchone()
    conn.close()
    if res is None:
        return 'Login failed'
    else:
        return 'Login succeeded, {0}'.format(res[0])

if __name__ == '__main__':
    print('please login')
    print('user: ', end='')
    user = input()
    print('password: ', end='')
    password = input()
    print(login(user, password))
