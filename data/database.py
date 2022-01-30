import sqlite3

SQLDATABASE = "data/database.db"

def execute(command, parameters=(), database=SQLDATABASE):
    connection = sqlite3.connect(database, timeout=10)
    cursor = connection.cursor()
    cursor.execute(command, parameters)
    connection.commit()
    connection.close()

def update_user(user_id, column, new_value):
    execute("insert or ignore into users(user_id) values(?)", (user_id,))
    execute("update users set %s = ? where user_id = ?" % column, (new_value, user_id))

def query(command, parameters=(), database=SQLDATABASE):
    connection = sqlite3.connect(database, timeout=10)
    cursor = connection.cursor()
    cursor.execute(command, parameters)
    data = cursor.fetchall()
    if len(data) == 0:
        return None
    else:
       result = data
    connection.close()
    return result

def lfmquery(database=SQLDATABASE):
    connection = sqlite3.connect(database, timeout=10)
    cursor = connection.cursor()
    cursor.execute("SELECT lastfm_username FROM users")
    data = cursor.fetchall()
    if len(data) == 0:
        return None
    else:
       result = data
    connection.close()
    return(" ".join("".join(data) for data in result).split(" "))

def dcquery(database=SQLDATABASE):
    connection = sqlite3.connect(database, timeout=10)
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM users")
    data = cursor.fetchall()
    if len(data) == 0:
        return None
    else:
       result = data
    connection.close()
    return("".join("".join(str(data) for data in result)).split(" "))

def get_user(userid):
    return query("select * from users where user_id = ?", (userid,))

def get_username(userid):
    return lfmquery("select * from users where lastfm_username = ?", (userid,))