import sqlite3


def crime_judge(tex):
    conn = sqlite3.connect('law.db')
    cursor = conn.execute("SELECT CRIMES from CRIME")
    crime = []
    for row in cursor:
        crime.append(row[0])
    conn.close()
    res = []
    for i in range(0, len(crime)):
        crime[i] = crime[i].replace("\n", "")
        n = tex.count(crime[i])
        if n > 0:
            res.append(crime[i])
    #print("刑事罪行认定如下: " + " ".join(res))
    return res


def cause_judge(tex):
    conn = sqlite3.connect('law.db')
    cursor = conn.execute("SELECT CAUSES from CAUSE")
    cause = []
    for row in cursor:
        cause.append(row[0])
    conn.close()
    res = []
    for i in range(0, len(cause)):
        cause[i] = cause[i].replace("\n", "")
        n = tex.count(cause[i])
        if n > 0:
            res.append(cause[i])
    #print("民事案由认定如下: " + " ".join(res))
    return res
